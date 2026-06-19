#!/usr/bin/env python

"""Compile probabilistic/non-deterministic domains into classical domains.

Outcome ordering is deliberately separated from outcome construction.  This
keeps the PPDDL source order intact by default and makes alternative ranking
heuristics explicit and reproducible.
"""

import argparse
import json
import math
import os
import time
from collections import OrderedDict
from dataclasses import dataclass
from itertools import product

from . import color
from .pddl import ast as pddl
from .pddl.domain import Action, Domain, Effect


SOURCE = "source"
PROBABILITY_DESC = "probability-desc"
EFFECT_COUNT_DESC = "effect-count-desc"
EFFECT_COUNT_ASC = "effect-count-asc"
RANKING_STRATEGIES = (
    SOURCE,
    PROBABILITY_DESC,
    EFFECT_COUNT_DESC,
    EFFECT_COUNT_ASC,
)
DEFAULT_RANKING = SOURCE
RANKING_CODES = {
    "0": SOURCE,
    "1": EFFECT_COUNT_ASC,
    "2": EFFECT_COUNT_DESC,
    "3": PROBABILITY_DESC,
}

# Maximum number of allowed single-outcome deterministic domains.
MAX_DOMAINS = 4096
PROBABILITY_EPSILON = 1e-9


@dataclass(frozen=True)
class Outcome:
    """A complete outcome together with metadata used only for ordering."""

    effect: Effect
    probability: object = None
    source_order: tuple = ()
    implicit: bool = False


@dataclass(frozen=True)
class CompiledAction:
    """A deterministic action and the outcome from which it was compiled."""

    action: Action
    outcome: Outcome


def normalize_ranking(ranking=DEFAULT_RANKING):
    """Validate and return a descriptive Python API ranking name."""

    if ranking is None:
        ranking = DEFAULT_RANKING
    if ranking not in RANKING_STRATEGIES:
        raise ValueError(
            "unknown ranking strategy {!r}; choose one of {}"
            .format(ranking, ", ".join(RANKING_STRATEGIES))
        )
    return ranking


def add_ranking_arguments(parser):
    """Add the shared ranking options to an :class:`argparse.ArgumentParser`."""

    parser.add_argument(
        "-r",
        "--ranking",
        choices=tuple(RANKING_CODES),
        default="0",
        metavar="MODE",
        help=("determinization order: 0=source (default), "
              "1=effect-count-asc, 2=effect-count-desc, "
              "3=probability-desc"),
    )


def resolve_cli_ranking(args):
    """Translate a numeric CLI mode into its descriptive strategy name."""

    value = getattr(args, "ranking", "0")
    if value in RANKING_STRATEGIES:
        return value
    args.ranking = RANKING_CODES[value]
    return args.ranking


def parse():
    usage = "python3 compilation.py <DOMAIN> [-r MODE] [-a] [-v]"
    description = "Compile a non-deterministic domain into classical domains."
    parser = argparse.ArgumentParser(
        usage=usage,
        description=description,
        allow_abbrev=False,
    )
    parser.add_argument("domain", type=str, help="path to a PDDL domain file")
    add_ranking_arguments(parser)
    parser.add_argument(
        "-a",
        "--all",
        help=("use only all-outcome compilation instead of both single-outcome "
              "and all-outcome compilation"),
        action="store_true",
        default=False,
    )
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    return parser.parse_args()


def _merge_effects(base, effects):
    if not isinstance(base, Effect):
        base = Effect()
    literals = list(base.literals)
    forall = list(base.forall)
    when = list(base.when)
    for effect in effects:
        literals.extend(effect.literals)
        forall.extend(effect.forall)
        when.extend(effect.when)
    return Effect(tuple(literals), tuple(forall), tuple(when))


def _neutral_effect(action):
    """Return a planner-friendly representation of a no-op outcome."""

    # Some classical planners reject actions with an empty effect.  Re-adding
    # ordinary precondition literals changes no state and represents a no-op.
    precondition_literals = getattr(action.preconditions, "literals", ())
    literals = tuple(
        literal for literal in precondition_literals
        if "=" not in str(literal)
    )
    return Effect(literals=literals)


def _validate_probability_block(action_name, block):
    total = 0.0
    for probability, _ in block:
        if not math.isfinite(probability) or probability < 0.0 or probability > 1.0:
            raise ValueError(
                "action {!r} has probability {} outside [0, 1]"
                .format(action_name, probability)
            )
        total += probability
    if total > 1.0 + PROBABILITY_EPSILON:
        raise ValueError(
            "action {!r} has a probabilistic block whose probabilities sum to {}"
            .format(action_name, total)
        )
    return total


def _probabilistic_outcomes(action):
    blocks = []
    for block_index, block in enumerate(action.probabilistic):
        total = _validate_probability_block(action.name, block)
        alternatives = [
            Outcome(
                effect=effect,
                probability=probability,
                source_order=(block_index, alternative_index),
            )
            for alternative_index, (probability, effect) in enumerate(block)
        ]
        residual = 1.0 - total
        if residual > PROBABILITY_EPSILON:
            # The residual alternative has no textual position.  Appending it
            # after explicit alternatives is the least surprising source order.
            alternatives.append(
                Outcome(
                    effect=Effect(),
                    probability=residual,
                    source_order=(block_index, len(block)),
                    implicit=True,
                )
            )
        blocks.append(tuple(alternatives))

    outcomes = []
    for combination in product(*blocks):
        effect = _merge_effects(action.effects, [item.effect for item in combination])
        if not effect:
            effect = _neutral_effect(action)
        outcomes.append(
            Outcome(
                effect=effect,
                probability=math.prod(item.probability for item in combination),
                source_order=tuple(
                    alternative_index
                    for item in combination
                    for alternative_index in item.source_order
                ),
                implicit=any(item.implicit for item in combination),
            )
        )
    return outcomes


def _oneof_outcomes(action):
    blocks = [
        tuple(
            Outcome(
                effect=effect,
                probability=None,
                source_order=(block_index, alternative_index),
            )
            for alternative_index, effect in enumerate(block)
        )
        for block_index, block in enumerate(action.oneof)
    ]

    outcomes = []
    for combination in product(*blocks):
        effect = _merge_effects(action.effects, [item.effect for item in combination])
        if not effect:
            effect = _neutral_effect(action)
        outcomes.append(
            Outcome(
                effect=effect,
                probability=None,
                source_order=tuple(
                    alternative_index
                    for item in combination
                    for alternative_index in item.source_order
                ),
            )
        )

    # A singleton ``oneof`` remains uncertain: it may apply its modeled effect
    # or leave only the unconditional effect. The implicit alternative follows
    # the modeled alternative in source mode.
    if len(outcomes) == 1:
        base_effect = action.effects if isinstance(action.effects, Effect) else Effect()
        if not base_effect:
            base_effect = _neutral_effect(action)
        outcomes.append(Outcome(
            effect=base_effect,
            probability=None,
            source_order=(len(blocks), 1),
            implicit=True,
        ))
    return outcomes


def _rank_outcomes(outcomes, ranking):
    # sorted() is stable, so the PPDDL source order resolves all score ties.
    if ranking == SOURCE:
        return tuple(outcomes)
    if ranking == PROBABILITY_DESC:
        return tuple(sorted(
            outcomes,
            key=lambda outcome: (
                outcome.probability is None,
                -(outcome.probability if outcome.probability is not None else 0.0),
            ),
        ))
    if ranking == EFFECT_COUNT_DESC:
        return tuple(sorted(outcomes, key=lambda outcome: len(outcome.effect), reverse=True))
    return tuple(sorted(outcomes, key=lambda outcome: len(outcome.effect)))


def _action_outcomes(action, ranking):
    if action.probabilistic and action.oneof:
        raise ValueError(
            "action {!r} mixes probabilistic and oneof effects; this is not supported"
            .format(action.name)
        )
    if action.probabilistic:
        outcomes = _probabilistic_outcomes(action)
    elif action.oneof:
        outcomes = _oneof_outcomes(action)
    else:
        effect = action.effects if action.effects else _neutral_effect(action)
        outcomes = [Outcome(effect=effect, probability=1.0, source_order=())]
    return _rank_outcomes(outcomes, ranking)


def _domain_probability_score(compiled_actions):
    """Return a stable log-probability score for a determinization."""

    score = 0.0
    for compiled in compiled_actions:
        probability = compiled.outcome.probability
        # oneof outcomes have no probability and retain source-order ties.
        if probability is None:
            continue
        if probability == 0.0:
            return float("-inf")
        score += math.log(probability)
    return score


def _rank_domains(domains, ranking):
    # The source order is already the lexicographic Cartesian-product order.
    # Stable global sorting makes probability/effect strategies describe the
    # complete deterministic domain rather than only each action in isolation.
    if ranking == SOURCE:
        return domains
    if ranking == PROBABILITY_DESC:
        return sorted(domains, key=_domain_probability_score, reverse=True)
    reverse = ranking == EFFECT_COUNT_DESC
    return sorted(
        domains,
        key=lambda compiled_actions: sum(
            len(compiled.outcome.effect) for compiled in compiled_actions
        ),
        reverse=reverse,
    )


###############################################################################
def compilation(
    domain,
    ranking=DEFAULT_RANKING,
    alloutcome=False,
):
    """Return deterministic domains compiled from ``domain``.

    ``ranking`` controls only ordering, never which explicit outcomes are
    retained. Residual probability is calculated from the PPDDL model.
    """

    ranking = normalize_ranking(ranking)

    # List of non-deterministic/probabilistic actions: key=name,
    # value=number of possible outcomes.
    nd_actions = OrderedDict()

    # Map generated deterministic action names back to source action names.
    map_actions = {}

    # One tuple of deterministic alternatives per source action.
    deterministic_actions = []

    for action in domain.actions:
        outcomes = _action_outcomes(action, ranking)
        map_actions[action.name] = action.name
        compiled_alternatives = []

        if len(outcomes) > 1:
            nd_actions[action.name] = len(outcomes)
            for index, outcome in enumerate(outcomes):
                name = "{}_{}".format(action.name, index)
                nd_actions[name] = len(outcomes)
                map_actions[name] = action.name
                compiled_alternatives.append(CompiledAction(
                    action=Action(
                        name=name,
                        parameters=tuple(zip(action.types, action.arg_names)),
                        preconditions=action.preconditions,
                        effects=outcome.effect,
                    ),
                    outcome=outcome,
                ))
        else:
            outcome = outcomes[0]
            compiled_alternatives.append(CompiledAction(
                action=Action(
                    name=action.name,
                    parameters=tuple(zip(action.types, action.arg_names)),
                    preconditions=action.preconditions,
                    effects=outcome.effect,
                ),
                outcome=outcome,
            ))

        deterministic_actions.append(tuple(compiled_alternatives))

    if not alloutcome:
        domains_product_len = math.prod(len(actions) for actions in deterministic_actions)
        if domains_product_len > MAX_DOMAINS:
            print(color.fg_yellow(
                "-- the possible combination of single-outcome domains is {}"
                .format(domains_product_len)
            ))
            print(color.fg_yellow(
                "-- that exceeds the allowed MAX_DOMAINS [{}]".format(MAX_DOMAINS)
            ))
            print(color.fg_yellow("-- switch to all-outcome compilation\n"))
            alloutcome = True
        elif domains_product_len > MAX_DOMAINS / 4:
            print(color.fg_green(
                "-- the possible combination of single-outcome domains is {}"
                .format(domains_product_len)
            ))
            print(color.fg_green("-- this degrades dramatically the planning performance"))
            print(color.fg_green(
                "-- recommended switching to all-outcome by giving the parameter '-a'\n"
            ))

    all_outcome_actions = tuple(
        compiled.action
        for alternatives in deterministic_actions
        for compiled in alternatives
    )

    if alloutcome:
        domain_actions = [all_outcome_actions]
    else:
        combinations = list(product(*deterministic_actions))
        combinations = _rank_domains(combinations, ranking)
        domain_actions = [
            tuple(compiled.action for compiled in combination)
            for combination in combinations
        ]
        # Keep the all-outcome determinization last: it is a fallback rather
        # than a single-outcome candidate and has no comparable probability.
        domain_actions.append(all_outcome_actions)

    domains = [
        Domain(
            name=domain.name,
            requirements=tuple(
                requirement for requirement in domain.requirements
                if requirement not in {":probabilistic-effects", ":non-deterministic"}
            ),
            types=domain.types,
            predicates=domain.predicates,
            derived_predicates=domain.derived_predicates,
            constants=domain.constants,
            actions=actions,
        )
        for actions in domain_actions
    ]
    return domains, nd_actions, map_actions


###############################################################################
def compile(
    domain,
    ranking=DEFAULT_RANKING,
    alloutcome=False,
    verbose=False,
):
    """Compile ``domain`` and write deterministic PDDL and metadata files."""

    ranking = normalize_ranking(ranking)
    deterministic_only = not (
        ":probabilistic-effects" in domain.requirements
        or ":non-deterministic" in domain.requirements
    )
    if deterministic_only and verbose:
        print(color.fg_yellow(
            "-- neither ':probabilistic-effects' nor ':non-deterministic' is present"
        ))
        print(color.fg_yellow(
            "-- '{}' is assumed to be deterministic".format(domain.name)
        ))

    deterministic_domains, nd_actions, map_actions = compilation(
        domain,
        ranking=ranking,
        alloutcome=True if deterministic_only else alloutcome,
    )

    domains_dir = "/tmp/safe-planner/{}{}/".format(
        domain.name, str(int(time.time() * 1000000))
    )
    os.makedirs(domains_dir, exist_ok=True)

    for index, deterministic_domain in enumerate(deterministic_domains):
        pddl_file = "{}/{}{:03d}.pddl".format(
            domains_dir, deterministic_domain.name, index + 1
        )
        with open(pddl_file, "w") as stream:
            stream.write(pddl.to_pddl(deterministic_domain))

    prob_file = "{}/{}.prob".format(domains_dir, domain.name)
    with open(prob_file, "w") as stream:
        json.dump(nd_actions, stream)

    map_file = "{}/{}.acts".format(domains_dir, domain.name)
    with open(map_file, "w") as stream:
        json.dump(map_actions, stream)

    if verbose:
        print(
            "{} deterministic domains generated in '{}' using '{}' ranking"
            .format(len(deterministic_domains), domains_dir, ranking)
        )

    return domains_dir


###############################################################################
if __name__ == "__main__":
    from safe_planner.pddl import parser as pddlparser

    args = parse()
    resolve_cli_ranking(args)
    parsed_domain = pddlparser.PDDLParser.parse(args.domain)
    if isinstance(parsed_domain, tuple):
        parsed_domain = parsed_domain[0]

    domains_dir = compile(parsed_domain, ranking=args.ranking, alloutcome=args.all)

    deterministic_domains = OrderedDict()
    nd_actions = OrderedDict()
    for domain_file in sorted(
        os.path.join(domains_dir, name) for name in os.listdir(domains_dir)
    ):
        if domain_file.endswith(".prob"):
            with open(domain_file) as stream:
                nd_actions = json.load(stream)
        elif domain_file.endswith(".pddl"):
            deterministic_domains[domain_file] = pddlparser.PDDLParser.parse(domain_file)
            print(color.fg_yellow("-- successfully parsed: ") + domain_file)

    print(
        color.fg_yellow("-- total number of non-deterministic domains: ")
        + str(len(deterministic_domains))
    )
    print(
        color.fg_yellow("-- non-deterministic actions: ")
        + str(set(nd_actions.values()))
    )

    if args.verbose:
        for deterministic_domain in deterministic_domains.values():
            print(color.fg_yellow("-------------------------"))
            print(pddl.to_pddl(deterministic_domain))

import pytest

from safe_planner import compilation
from safe_planner import cli
from safe_planner.pddl.domain import Action, Domain, Effect, Precondition
from safe_planner.pddl.parser import PDDLParser


def effect(*names):
    return Effect(literals=tuple((name,) for name in names))


def probabilistic_action(name="act", probabilities=(0.2, 0.7)):
    alternatives = (
        (probabilities[0], effect("first", "first-extra")),
        (probabilities[1], effect("second")),
    )
    return Action(
        name=name,
        preconditions=Precondition(literals=(("ready",),)),
        effects=effect("base"),
        probabilistic=(alternatives,),
    )


def make_domain(*actions):
    return Domain(
        name="ranking",
        requirements=(":probabilistic-effects",),
        actions=actions,
    )


def single_outcome_effects(domain, ranking):
    domains, _, _ = compilation.compilation(domain, ranking=ranking)
    # The final domain is the all-outcome fallback.
    return [item.actions[0].effects.literals for item in domains[:-1]]


def test_source_ranking_preserves_pddl_alternative_order_and_appends_residual():
    effects = single_outcome_effects(
        make_domain(probabilistic_action()),
        compilation.SOURCE,
    )

    assert effects == [
        (("base",), ("first",), ("first-extra",)),
        (("base",), ("second",)),
        (("base",),),
    ]


def test_source_ranking_preserves_order_from_parsed_pddl(tmp_path):
    domain_file = tmp_path / "domain.pddl"
    domain_file.write_text(
        """
        (define (domain source-order)
          (:requirements :probabilistic-effects :strips)
          (:predicates (ready) (first) (second) (last))
          (:action modeled-first
            :precondition (ready)
            :effect (probabilistic 0.2 (first) 0.7 (second)))
          (:action modeled-second
            :precondition (ready)
            :effect (last)))
        """,
        encoding="utf-8",
    )
    parsed = PDDLParser.parse(str(domain_file))

    domains, _, _ = compilation.compilation(parsed, ranking=compilation.SOURCE)

    assert tuple(action.name for action in domains[0].actions) == (
        "modeled-first_0",
        "modeled-second",
    )
    assert domains[0].actions[0].effects.literals[0][0] == "first"
    assert domains[1].actions[0].effects.literals[0][0] == "second"
    assert domains[2].actions[0].effects.literals[0][0] == "ready"


def test_probability_ranking_uses_actual_residual_probability():
    effects = single_outcome_effects(
        make_domain(probabilistic_action()),
        compilation.PROBABILITY_DESC,
    )

    assert effects == [
        (("base",), ("second",)),       # 0.7
        (("base",), ("first",), ("first-extra",)),  # 0.2
        (("base",),),                   # residual 0.1
    ]


@pytest.mark.parametrize(
    "ranking, expected",
    [
        (
            compilation.EFFECT_COUNT_DESC,
            [
                (("base",), ("first",), ("first-extra",)),
                (("base",), ("second",)),
                (("base",),),
            ],
        ),
        (
            compilation.EFFECT_COUNT_ASC,
            [
                (("base",),),
                (("base",), ("second",)),
                (("base",), ("first",), ("first-extra",)),
            ],
        ),
    ],
)
def test_effect_count_strategies_are_explicit_and_stable(ranking, expected):
    assert single_outcome_effects(
        make_domain(probabilistic_action()), ranking
    ) == expected


def test_probability_ranking_orders_complete_domains_by_joint_probability():
    first = Action(
        name="first-action",
        preconditions=Precondition(literals=(("ready",),)),
        probabilistic=((
            (0.6, effect("a0")),
            (0.4, effect("a1")),
        ),),
    )
    second = Action(
        name="second-action",
        preconditions=Precondition(literals=(("ready",),)),
        probabilistic=((
            (0.99, effect("b0")),
            (0.01, effect("b1")),
        ),),
    )

    domains, _, _ = compilation.compilation(
        make_domain(first, second),
        ranking=compilation.PROBABILITY_DESC,
    )

    assert [tuple(action.name for action in domain.actions) for domain in domains[:-1]] == [
        ("first-action_0", "second-action_0"),  # 0.594
        ("first-action_1", "second-action_0"),  # 0.396
        ("first-action_0", "second-action_1"),  # 0.006
        ("first-action_1", "second-action_1"),  # 0.004
    ]


def test_source_ranking_uses_lexicographic_cartesian_product_order():
    first = Action(
        name="first-action",
        preconditions=Precondition(literals=(("ready",),)),
        oneof=((effect("a0"), effect("a1")),),
    )
    second = Action(
        name="second-action",
        preconditions=Precondition(literals=(("ready",),)),
        oneof=((effect("b0"), effect("b1")),),
    )

    domains, _, _ = compilation.compilation(
        make_domain(first, second),
        ranking=compilation.SOURCE,
    )

    assert [tuple(action.name for action in domain.actions) for domain in domains[:-1]] == [
        ("first-action_0", "second-action_0"),
        ("first-action_0", "second-action_1"),
        ("first-action_1", "second-action_0"),
        ("first-action_1", "second-action_1"),
    ]


def test_singleton_oneof_keeps_implicit_noop_after_source_outcome():
    action = Action(
        name="act",
        preconditions=Precondition(literals=(("ready",),)),
        oneof=((effect("done"),),),
    )

    domains, nd_actions, _ = compilation.compilation(make_domain(action))

    assert nd_actions["act"] == 2
    assert domains[0].actions[0].effects.literals == (("done",),)
    assert domains[1].actions[0].effects.literals == (("ready",),)


def test_implicit_noop_is_retained_for_multiple_outcomes_without_base_effect():
    action = Action(
        name="act",
        preconditions=Precondition(literals=(("ready",),)),
        probabilistic=((
            (0.2, effect("first")),
            (0.3, effect("second")),
        ),),
    )

    domains, nd_actions, _ = compilation.compilation(
        make_domain(action), ranking=compilation.SOURCE
    )

    assert nd_actions["act"] == 3
    assert domains[2].actions[0].effects.literals == (("ready",),)


def test_complete_single_outcome_distribution_does_not_gain_a_noop():
    action = Action(
        name="act",
        preconditions=Precondition(literals=(("ready",),)),
        probabilistic=(((1.0, effect("done")),),),
    )

    domains, nd_actions, _ = compilation.compilation(make_domain(action))

    assert not nd_actions
    assert len(domains) == 2
    assert domains[0].actions[0].name == "act"
    assert domains[0].actions[0].effects.literals == (("done",),)


def test_invalid_probability_sum_is_rejected():
    action = probabilistic_action(probabilities=(0.6, 0.5))

    with pytest.raises(ValueError, match="probabilities sum"):
        compilation.compilation(make_domain(action))


def test_unknown_ranking_is_rejected():
    with pytest.raises(ValueError, match="unknown ranking strategy"):
        compilation.compilation(make_domain(probabilistic_action()), ranking="mystery")


def test_main_cli_defaults_to_source():
    parser = cli.parse_args()

    default_args = parser.parse_args(["domain.pddl", "problem.pddl"])
    compilation.resolve_cli_ranking(default_args)
    assert default_args.ranking == compilation.SOURCE


@pytest.mark.parametrize(
    "flag, mode, expected",
    [
        ("-r", "0", compilation.SOURCE),
        ("-r", "1", compilation.EFFECT_COUNT_ASC),
        ("--ranking", "2", compilation.EFFECT_COUNT_DESC),
        ("--ranking", "3", compilation.PROBABILITY_DESC),
    ],
)
def test_main_cli_maps_numeric_ranking_modes(flag, mode, expected):
    args = cli.parse_args().parse_args([
        "domain.pddl",
        "problem.pddl",
        flag,
        mode,
    ])

    compilation.resolve_cli_ranking(args)

    assert args.ranking == expected


def test_main_cli_rejects_unknown_numeric_ranking_mode():
    with pytest.raises(SystemExit):
        cli.parse_args().parse_args([
            "domain.pddl",
            "problem.pddl",
            "-r",
            "4",
        ])


def test_main_cli_rejects_removed_rank_option():
    with pytest.raises(SystemExit):
        cli.parse_args().parse_args([
            "domain.pddl",
            "problem.pddl",
            "--rank",
            "1",
        ])


def test_boolean_ranking_is_not_supported():
    with pytest.raises(ValueError, match="unknown ranking strategy"):
        compilation.compilation(make_domain(probabilistic_action()), ranking=True)

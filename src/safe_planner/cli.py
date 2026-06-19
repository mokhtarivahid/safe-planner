#!/usr/bin/env python
"""Command-line entry point for Safe-Planner.

Wires the FOND planner (:mod:`safe_planner.planner`) to the various output
formatters in :mod:`safe_planner.io` and exposes argparse flags for the
planner race (`-c`), profile overrides (`--profile`), policy rendering
(`-d`, `-m`, `--render`), determinization ordering (`--ranking`),
structured reports (`-s`) and feedback
(`--summary`, `--no-color`).

The CLI exit code mirrors the policy verdict (0=solved/trivial, 3=partial,
4=unsolved) so it can be consumed by shell pipelines / CI.
"""

import argparse
import os
import sys

from . import color
from . import compilation
from . import planner
from .io import dot_plan, report as report_io
from .planners import registry

# Recursion limit kept generous because get_paths() still recurses on policies
# with many branches; remove_path() is now iterative and does not need it.
sys.setrecursionlimit(20000)


def parse_args(dir_path=''):
    usage = ('safe-planner <DOMAIN> <PROBLEM> [-c <PLANNERS>] '
             '[-r MODE] [-a] [-p] '
             '[-d] [-m] [--render FMT] [-j] [-s] [--summary] [--no-color] '
             '[-V] [--val-timeout SECS] [--val-epsilon EPS] [--val-verbose] '
             '[-v N] [-h]')
    description = "Safe-Planner is a non-deterministic planner for PPDDL."
    parser = argparse.ArgumentParser(
        usage=usage,
        description=description,
        allow_abbrev=False,
    )

    parser.add_argument('domain',  nargs='?', type=str, help='path to a PDDL domain file')
    parser.add_argument('problem', nargs='?', type=str, help='path to a PDDL problem file')

    parser.add_argument("-c", "--planners", nargs='+', type=str, default=["ff"],
        choices=registry.cli_choices(), metavar='PLANNER',
        help="a list of classical planners (default=[ff]). Available: "
             + ", ".join(registry.available_planners()))
    parser.add_argument("--profile", action="append", default=None, metavar="PLANNER:NAME",
        help="select a non-default argument profile for a planner (repeatable), "
             "e.g. '--profile fd:satisficing-lama-first --profile ff:default'. "
             "Use --list-profiles to see what is available.")
    parser.add_argument("--list-profiles", nargs="?", const="__all__", default=None,
        metavar="PLANNER",
        help="list the argument profiles defined in pddl-solvers' "
             "planner_profiles.yaml and exit. Pass a planner name to "
             "filter (e.g. '--list-profiles fd'); omit to list all planners.")
    compilation.add_ranking_arguments(parser)
    parser.add_argument("-a", "--all-outcome", action="store_true", default=False,
        help="use only the all-outcome compilation strategy (skip single-outcome).")
    parser.add_argument("-sp", "--safe-planner", action="store_true", default=False,
        help="switch to the (unsound) SP algorithm (default=NDP2).")

    # ---- output / representation ----
    parser.add_argument("-d", "--dot", action="store_true",
        help="draw a graph of the produced policy into a GraphViz dot file")
    parser.add_argument("--render", choices=("svg", "pdf", "png"), default=None,
        help="rasterise/vectorise generated dot files via `dot` (requires graphviz)")
    parser.add_argument("-p", "--path", action="store_true",
        help="print out possible execution paths of the produced policy")
    parser.add_argument("-j", "--json", action="store_true",
        help="emit the produced policy as a JSON file (legacy schema)")
    parser.add_argument("-s", "--store", action="store_true",
        help="store a structured run report next to the problem file (.stat.json)")
    parser.add_argument("--summary", action="store_true",
        help="print a colour-aware end-of-run summary with verdict and hints")
    parser.add_argument("--no-color", action="store_true",
        help="disable ANSI colour escapes regardless of TTY / env vars")

    parser.add_argument("-v", "--verbose", default=0, type=int, choices=(0, 1, 2),
        help="0=minimal, 1=high-level, 2=external planners output (default=0)")

    # ---- optional VAL plan validation (per-call, expensive) ----
    # VAL validates classical plans only. Safe-Planner builds FOND policies 
    # (conditional trees) so we cannot validate the *final* policy directly; 
    # instead, with -V we validate every internal classical planning call performed 
    # during the FOND replanning loop. This is expensive but useful for debugging.
    parser.add_argument("-V", "--validate", action="store_true",
        help="validate every internal classical plan with VAL (requires "
             "VAL to be built: cd third_party/pddl-solvers && ./build_all.sh --planner val). "
             "NOTE: this is expensive and runs once per internal planning call.")
    parser.add_argument("--val-timeout", type=int, default=60, metavar="SECS",
        help="timeout in seconds for each VAL invocation (default: 60)")
    parser.add_argument("--val-epsilon", type=float, default=None, metavar="EPS",
        help="epsilon tolerance passed to VAL via -t (auto-set for temporal plans)")
    parser.add_argument("--val-verbose", action="store_true",
        help="pass -v to VAL for verbose plan-check reporting")

    # ---- planner backend selection ----
    parser.add_argument("--direct", action="store_true",
        help="call planner binaries directly (legacy path) instead of routing "
             "through pddl-solvers/run_planner.py. In direct mode VAL (-V) is "
             "invoked independently after each classical call.")

    return parser


def parse_relative_path():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    parser = parse_args(dir_path)
    args = parser.parse_args()

    # --list-profiles is informational; it short-circuits before any planning
    # so users can introspect the catalogue even without a domain/problem.
    if args.list_profiles is not None:
        _print_profiles(None if args.list_profiles == "__all__" else args.list_profiles)
        sys.exit(0)

    if args.domain is None:
        parser.print_help()
        sys.exit()

    compilation.resolve_cli_ranking(args)

    if not os.path.isabs(args.domain):
        args.domain = os.path.abspath(args.domain)
    if args.problem is not None and not os.path.isabs(args.problem):
        args.problem = os.path.abspath(args.problem)

    if args.problem is None:
        with open(args.domain) as f:
            data = f.read()
        if not all(x in data for x in ['(problem', '(domain']):
            args.problem = args.domain
            args.domain = os.path.join(os.path.dirname(args.domain), 'domain.pddl')

    if not os.path.isfile(args.domain):
        print(color.fg_yellow("the domain file '{}' does not exist".format(args.domain)))
        print(color.fg_yellow("pass the absolute path of the domain file"))
        sys.exit(2)

    return args, parser


def _print_profiles(planner_filter):
    """Print the planner-profile catalogue to stdout.

    Pass ``None`` to dump every planner known to the registry, or a planner
    name to restrict the output to that planner only.
    """
    from .planners import profiles as profiles_mod
    cat = profiles_mod.profiles
    axiom_map = profiles_mod._AXIOM_SAFE_PROFILES

    if planner_filter is None:
        targets = list(registry.available_planners())
    else:
        targets = [registry.canonical_name(planner_filter)]

    for planner in targets:
        names = cat.list_configs(planner)
        if not names:
            print("{}: <no profiles>".format(color.fg_yellow(planner)))
            continue
        default = cat.default_name(planner)
        axiom_safe = set(axiom_map.get(planner, ()))
        print(color.fg_yellow(planner) + ":")
        configs = cat.configs(planner)
        for idx, name in enumerate(names):
            cfg = configs.get(name, {})
            marker = " *" if name == default else "  "
            tag = " [axiom-safe]" if name in axiom_safe else ""
            if "search" in cfg:
                detail = "search={}".format(cfg["search"])
            else:
                detail = "args={}".format(" ".join(str(a) for a in cfg.get("args", []) or []) or "<none>")
            print("  [{}]{} {:<28} {}{}".format(idx, marker, name, detail, tag))
        print("")
    print(color.fg_yellow("(*) = current default; override via --profile PLANNER:NAME"))
    print(color.fg_yellow("[axiom-safe] = profile supports :derived predicates (auto-selected on such domains)"))


def _apply_profiles(profiles):
    if not profiles:
        return
    from .planners import profiles as profiles_mod
    cat = profiles_mod.profiles
    for raw in profiles:
        if ":" not in raw:
            print(color.fg_red("ignoring malformed --profile '{}': expected PLANNER:NAME".format(raw)))
            continue
        planner_name, profile_name = raw.split(":", 1)
        try:
            idx = cat.set_default(planner_name.strip(), profile_name.strip())
            print(color.fg_yellow("-- profile override: ")
                  + "{} -> {} (index {})".format(planner_name, profile_name, idx))
        except (KeyError, ValueError) as exc:
            print(color.fg_red("invalid --profile '{}': {}".format(raw, exc)))


def _apply_validation(args):
    """Configure VAL based on the selected planner backend.

    * Default (``run_planner``) backend: forward the flags to
      ``run_planner.py`` via :data:`runner.VAL_CONFIG`.
    * Direct backend: populate :data:`validation.CONFIG` so the
      in-process VAL wrapper runs after every classical call.
    """
    if not getattr(args, "validate", False):
        return
    from .planners import runner as _runner
    if _runner.BACKEND == "direct":
        from .planners import validation as val_mod
        val_mod.CONFIG.enabled = True
        val_mod.CONFIG.timeout = args.val_timeout
        val_mod.CONFIG.epsilon = args.val_epsilon
        val_mod.CONFIG.verbose = args.val_verbose
        exe = val_mod.get_val_executable("Validate")
        if exe is None:
            print(color.fg_red(
                "-- --validate requested but VAL 'Validate' was not found at "
                "third_party/pddl-solvers/VAL/build/bin/Validate."))
            print(color.fg_yellow(
                "   build it with: cd third_party/pddl-solvers && "
                "./build_all.sh --planner val"))
        else:
            print(color.fg_yellow("-- VAL plan validation enabled (direct, in-process): ") + str(exe))
    else:
        _runner.VAL_CONFIG.enabled = True
        _runner.VAL_CONFIG.timeout = args.val_timeout
        _runner.VAL_CONFIG.epsilon = args.val_epsilon
        _runner.VAL_CONFIG.verbose = args.val_verbose
        print(color.fg_yellow(
            "-- VAL plan validation enabled (forwarded to pddl-solvers/run_planner.py)"))


def _apply_backend(args):
    """Switch the planner runner backend before any planner call."""
    if getattr(args, "direct", False):
        from .planners import runner as _runner
        _runner.BACKEND = "direct"
        print(color.fg_yellow("-- planner backend: ") + "direct (legacy)")


def _render_dot(dot_file, fmt):
    import shutil, subprocess
    if shutil.which("dot") is None:
        print(color.fg_red("graphviz `dot` not found in PATH; skipping --render for " + dot_file))
        return None
    out = "{}.{}".format(dot_file, fmt)
    try:
        subprocess.run(["dot", "-T{}".format(fmt), dot_file, "-o", out],
                       check=True, timeout=60)
        print(color.fg_yellow("-- {} render: ".format(fmt)) + out)
        return out
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        print(color.fg_red("dot render failed: {}".format(exc)))
        return None


def main():
    args, _ = parse_relative_path()

    if args.no_color:
        color.set_enabled(False)

    _apply_profiles(args.profile)
    _apply_backend(args)
    _apply_validation(args)

    policy = planner.Planner(
        args.domain,
        args.problem,
        planners=args.planners,
        safe_planner=args.safe_planner,
        ranking=args.ranking,
        alloutcome=args.all_outcome,
        verbose=args.verbose,
    )
    plan = policy.plan()
    verdict = report_io.classify_plan(plan)

    # `--render FMT` is a rendering directive: always enable the GraphViz
    # pipeline so we can produce <fmt> via `dot` regardless of other flags.
    if args.render:
        args.dot = True

    policy.print_plan(del_effect_inc=True, det_effect_inc=False)

    if args.path:
        paths = policy.get_paths(plan)
        policy.print_paths(paths=paths, del_effect_inc=True)
        if args.dot:
            pa = set(policy.prob_actions) if policy.prob_actions else set()
            for i, path in enumerate(paths):
                dot_file = dot_plan.gen_dot_plan(plan=path, prob_actions=pa)
                print(color.fg_yellow('-- path{} dot file: ').format(i + 1) + dot_file)
                if args.render:
                    _render_dot(dot_file, args.render)
            dot_plan.gen_dot_plan(plan=paths[0], prob_actions=pa)
            print('')

    if args.dot:
        tree = policy.plan(tree=True)
        dot_file = dot_plan.gen_dot_plan(plan=tree, del_effect=True,
                                         domain_file=args.domain,
                                         problem_file=args.problem,
                                         prob_actions=set(policy.prob_actions) if policy.prob_actions else set())
        print(color.fg_yellow('-- dot file: ') + dot_file + '\n')
        if args.render:
            _render_dot(dot_file, args.render)

    if args.json:
        from .io import json_ma_plan
        from .io import dot_ma_plan
        json_output = json_ma_plan.json_ma_plan(policy, verbose=args.verbose)
        if json_output is not None:
            plan_json_file, actions_json_file = json_output
            print(color.fg_yellow('-- plan_json_file:') + plan_json_file)
            print(color.fg_yellow('-- actions_json_file:') + actions_json_file)
            dot_file, tred_dot_file = dot_ma_plan.parallel_plan(policy, verbose=args.verbose)
            print(color.fg_yellow('-- graphviz file: ') + dot_file)
            print(color.fg_yellow('-- transitive reduction: ') + tred_dot_file)

        from .io import json_plan
        json_file, _ = json_plan.json_plan(policy)
        print(color.fg_yellow('\n-- json file: ') + json_file)

    if args.store:
        out = report_io.write_run_report(
            policy, plan=plan,
            planners=list(args.planners),
            arguments=sys.argv[1:],
        )
        print(color.fg_yellow('-- run report: ') + out)

    print('')
    if args.problem is not None:
        print('Planning domain: %s' % policy.domain_file)
        print('Planning problem: %s' % policy.problem_file)
    else:
        print('Planning problem: %s' % policy.domain_file)
    print('Arguments: %s' % ' '.join(sys.argv[1:]))
    print('Verdict: %s' % verdict.upper())
    print('Policy length: %i' % len(policy.policy))
    print('Plan length: %i' % max(0, len(plan) - 1))
    print('Compilation time: %.3f s [%i domains]' % (policy.compilation_time, len(policy.domains)))
    print('Planning time: %.3f s' % policy.planning_time)
    print('Planning iterations (all-outcome): %i' % policy.alloutcome_planning_call)
    print('Total number of replannings (single-outcome): %i' % policy.singleoutcome_planning_call)
    print('Total number of unsolvable states: %i' % len(policy.unsolvable_states))

    # Direct-backend VAL summary (run_planner backend prints per-call instead).
    from .planners import runner as _runner
    if _runner.BACKEND == "direct":
        from .planners import validation as _val
        val_summary = _val.summary_line()
        if val_summary is not None:
            print(val_summary)

    if args.summary or verdict != "solved":
        print('')
        print(report_io.render_summary(policy, plan))

    sys.exit({"solved": 0, "trivial": 0, "partial": 3, "unsolved": 4}.get(verdict, 1))


if __name__ == '__main__':
    main()

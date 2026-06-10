"""Structured policy and run reports for Safe-Planner.

This module provides:

* :func:`build_policy_report` — produce a deterministic, machine-readable
  description of the produced policy (states, steps, outcomes, transitions,
  reachability classification, statistics).
* :func:`build_run_report` — extend a policy report with timing,
  call counts, planner configuration, and a final verdict
  (``solved`` / ``partial`` / ``unsolved`` / ``trivial``).
* :func:`write_run_report` — persist the run report next to the problem file
  as ``<problem>.stat.json`` and (when requested) also emit a CSV row.
* :func:`render_summary` — human-friendly, colour-aware textual summary.

The schema version is bumped whenever the JSON shape changes, so downstream
tools can pin to a known structure.
"""

from __future__ import annotations

import json
import os
import sys
import time
from collections import OrderedDict
from typing import Any, Dict, List, Optional, Tuple

from .. import color

SCHEMA_VERSION = "2.0"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _atom_to_str(atom) -> str:
    """Render a PDDL atom tuple as ``(pred arg1 arg2 ...)``."""
    try:
        return "({})".format(" ".join(str(x) for x in atom))
    except TypeError:
        return str(atom)


def _step_actions(step) -> Tuple[Tuple[str, ...], ...]:
    """Normalise a planning step to a tuple of action signatures."""
    if step is None or step == "GOAL":
        return tuple()
    return tuple(tuple(map(str, a)) for a in step)


def _step_as_str(step) -> List[str]:
    return ["({})".format(" ".join(a)) for a in _step_actions(step)]


# ---------------------------------------------------------------------------
# Plan classification
# ---------------------------------------------------------------------------

def classify_plan(plan: Dict[Any, Any]) -> str:
    """Return a coarse classification of a plan.

    * ``"trivial"`` — the initial state already satisfies the goal.
    * ``"solved"`` — every terminal leaf is a goal (strong-cyclic policy).
    * ``"partial"`` — at least one ``GOAL`` reached but some leaves dangling.
    * ``"unsolved"`` — no goal reachable from the initial state.
    """
    if not plan:
        return "unsolved"
    if plan.get(0) == "GOAL":
        return "trivial"
    has_goal = any(v == "GOAL" for v in plan.values()) or "GOAL" in plan
    has_dead = any(v is None for v in plan.values())
    if has_goal and not has_dead:
        return "solved"
    if has_goal and has_dead:
        return "partial"
    return "unsolved"


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

def build_policy_report(policy, plan: Optional[Dict[Any, Any]] = None) -> Dict[str, Any]:
    """Produce a JSON-serialisable description of the produced policy."""
    if plan is None:
        plan = policy.plan()

    nodes: Dict[str, Any] = {}
    for level, step in plan.items():
        # Skip the terminal goal state; it is represented as a target in transitions
        if level == "GOAL" or step == "GOAL":
            continue

        node_id = str(level)
        if step is None:
            # Dead-end states are represented as nodes with no transitions
            nodes[node_id] = {
                "actions": [],
                "transitions": [],
            }
            continue

        actions, outcomes = step
        transitions: List[Dict[str, Any]] = []
        for (conditions, jump) in outcomes:
            add_atoms: List[str] = []
            del_atoms: List[str] = []
            if conditions:
                try:
                    add_atoms = [_atom_to_str(a) for a in conditions[0]]
                    del_atoms = [_atom_to_str(a) for a in conditions[1]]
                except (IndexError, TypeError):
                    pass

            transitions.append({
                "effects": {"add": add_atoms, "del": del_atoms},
                "target": "GOAL" if jump == "GOAL" else str(jump),
            })

        nodes[node_id] = {
            "actions": [_atom_to_str(a.sig) if hasattr(a, "sig") else str(a)
                        for a in actions],
            "transitions": transitions,
        }

    report: Dict[str, Any] = {
        "version": "2.0",
        "type": "fond-policy",
        "root": "0",
        "verdict": classify_plan(plan),
        "policy_length": len(policy.policy),
        "plan_length": max(0, len(plan) - 1),
        "nodes": nodes,
    }

    return report


def build_run_report(policy, plan: Optional[Dict[Any, Any]] = None,
                     planners: Optional[List[str]] = None,
                     arguments: Optional[List[str]] = None) -> Dict[str, Any]:
    """Extend :func:`build_policy_report` with run-level metadata."""
    if plan is None:
        plan = policy.plan()
    report = build_policy_report(policy, plan)

    report["safe_planner"] = {
        "domain_file": policy.domain_file,
        "problem_file": policy.problem_file,
        "domain": getattr(policy.domain, "name", None),
        "problem": getattr(policy.problem, "problem", None),
        "arguments": list(arguments) if arguments is not None else list(sys.argv[1:]),
        "planners": list(planners) if planners is not None else list(policy.planners),
        "deterministic_domains": len(policy.domains),
        "non_deterministic_actions": sorted(set(policy.prob_actions)) if policy.prob_actions else [],
        "timings_seconds": {
            "compilation": round(policy.compilation_time, 6),
            "planning": round(policy.planning_time, 6),
        },
        "calls": {
            "all_outcome_iterations": policy.alloutcome_planning_call,
            "single_outcome_replannings": policy.singleoutcome_planning_call,
        },
        "unsolvable_states": len(policy.unsolvable_states),
        "timestamp": int(time.time()),
    }
    return report


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def _stat_path(policy) -> str:
    base = policy.problem_file or policy.domain_file
    return "{}.stat.json".format(os.path.splitext(base)[0])


def write_run_report(policy, plan: Optional[Dict[Any, Any]] = None,
                     path: Optional[str] = None,
                     csv_append: bool = False,
                     planners: Optional[List[str]] = None,
                     arguments: Optional[List[str]] = None) -> str:
    """Write the structured JSON report and optionally append a CSV row."""
    report = build_run_report(policy, plan, planners=planners, arguments=arguments)
    path = path or _stat_path(policy)
    with open(path, "w") as fp:
        json.dump(report, fp, indent=2)

    if csv_append and policy.domain_file:
        csv_file = os.path.join(os.path.dirname(policy.domain_file) or ".", "results.csv")
        header = ("problem_file,problem,verdict,planning_time,compilation_time,"
                  "single_outcome_calls,all_outcome_calls,unsolvable_states,"
                  "policy_length,plan_length,n_domains\n")
        new = not os.path.exists(csv_file)
        try:
            with open(csv_file, "a") as fp:
                if new:
                    fp.write(header)
                fp.write("{},{},{},{:.3f},{:.3f},{},{},{},{},{},{}\n".format(
                    os.path.basename(policy.problem_file) if policy.problem_file else "",
                    getattr(policy.problem, "problem", "") or "",
                    report["verdict"],
                    policy.planning_time,
                    policy.compilation_time,
                    policy.singleoutcome_planning_call,
                    policy.alloutcome_planning_call,
                    len(policy.unsolvable_states),
                    len(policy.policy),
                    max(0, len(plan or policy.plan()) - 1),
                    len(policy.domains),
                ))
        except OSError:
            # Read-only benchmarks dir — silently skip the CSV side-effect.
            pass

    return path


# ---------------------------------------------------------------------------
# Human-readable summary
# ---------------------------------------------------------------------------

_VERDICT_HINTS = {
    "solved": ("SOLVED",  color.fg_green,
               "Strong-cyclic policy found; every reachable leaf is a goal."),
    "partial": ("PARTIAL", color.fg_yellow,
                "Goal reachable from some outcomes; some leaves remain dead-ends "
                "(weak / cyclic-but-not-strong policy)."),
    "trivial": ("TRIVIAL", color.fg_yellow,
                "Initial state already satisfies the goal; empty plan."),
    "unsolved": ("UNSOLVED", color.fg_red,
                 "No plan found at the initial state. Try a different planner "
                 "(-c ff fd madagascar), the all-outcome mode (-a), or check the "
                 "PPDDL for unreachable goals."),
}


def render_summary(policy, plan: Optional[Dict[Any, Any]] = None) -> str:
    """Return a coloured, human-readable run summary."""
    if plan is None:
        plan = policy.plan()
    verdict = classify_plan(plan)
    label, paint, hint = _VERDICT_HINTS[verdict]

    lines = []
    lines.append(color.bg_yellow("RUN SUMMARY"))
    lines.append("  Verdict          : {}".format(paint(label)))
    lines.append("  Hint             : {}".format(hint))
    lines.append("  Domain           : {}".format(policy.domain_file or "-"))
    lines.append("  Problem          : {}".format(policy.problem_file or policy.domain_file or "-"))
    lines.append("  Planners         : {}".format(", ".join(policy.planners) or "-"))
    lines.append("  Det. domains     : {}".format(len(policy.domains)))
    if policy.prob_actions:
        lines.append("  ND actions       : {}".format(len(set(policy.prob_actions))))
    lines.append("  Policy length    : {}".format(len(policy.policy)))
    lines.append("  Plan levels      : {}".format(max(0, len(plan) - 1)))
    lines.append("  Unsolvable states: {}".format(len(policy.unsolvable_states)))
    lines.append("  Replannings      : {} (single-outcome) / {} (all-outcome)".format(
        policy.singleoutcome_planning_call, policy.alloutcome_planning_call))
    lines.append("  Compilation time : {:.3f} s".format(policy.compilation_time))
    lines.append("  Planning time    : {:.3f} s".format(policy.planning_time))
    return "\n".join(lines)

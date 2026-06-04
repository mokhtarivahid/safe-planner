#!/usr/bin/env python
"""Unified planner dispatcher built on top of ``pddl-solvers/run_planner.py``.

Every classical planning call performed by Safe-Planner during its FOND
replanning loop is routed through ``third_party/pddl-solvers/run_planner.py``.
That script knows how to invoke each planner binary, applies the requested
profile from ``planner_profiles.yaml`` and -- when ``-V`` is supplied --
runs VAL on the returned plan. The result is returned to us as a JSON
document which we convert into Safe-Planner's internal plan format
(``list[list[tuple[str, ...]]]``).

Public entry points
-------------------
``Plan(planners, domain, problem, pwd, verbose=False)``
    Race several planners; return the first plan found.
``kill_jobs(pwd, planners)``
    Terminate any leftover child processes (used by callers on shutdown).
``VAL_CONFIG``
    Module-level :class:`ValidationConfig`; the CLI populates it from
    ``-V/--val-*`` flags and we forward those onto ``run_planner.py``.
"""

from __future__ import annotations

import json
import os
import re
import signal
import subprocess
import sys
import tempfile
import uuid
from dataclasses import dataclass
from multiprocessing import Array, Process, Queue
from pathlib import Path
from typing import Iterable

from .. import color
from . import registry
from .profiles import profiles, _YAML_ALIASES


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_RUN_PLANNER = registry.REPO_ROOT / "third_party" / "pddl-solvers" / "run_planner.py"

# Per-call timeout (seconds) forwarded to ``run_planner.py -t``. Each
# individual classical call inside the FOND loop must finish within this
# budget. The FOND loop itself has its own outer timeout managed by
# ``planner.py``.
DEFAULT_TIMEOUT = 1800


@dataclass
class ValidationConfig:
    """Per-call VAL options forwarded to ``run_planner.py``.

    The CLI populates this singleton when ``-V/--validate`` is given. The
    fields map 1:1 onto ``run_planner.py``'s ``--val-*`` flags.
    """

    enabled: bool = False
    timeout: int = 60
    epsilon: float | None = None
    verbose: bool = False


VAL_CONFIG = ValidationConfig()


# ---------------------------------------------------------------------------
# Process management (used by the multiprocessing race in ``Plan``)
# ---------------------------------------------------------------------------

def kill_pid(pid: int) -> int:
    """Kill a child process-group by pid (no-op if it's already gone)."""
    if pid == 0:
        return 0
    try:
        os.killpg(pid, 0)
    except OSError:
        return 0
    try:
        os.killpg(pid, signal.SIGTERM)
    except OSError:
        return 0
    return 0


def kill_jobs(pwd: str, planners: Iterable[str]) -> None:
    """Terminate any leftover subprocesses recorded in ``<pwd>/<planner>-pid.txt``."""
    for planner in planners:
        pid_file = '%s/%s-pid.txt' % (pwd, planner)
        try:
            with open(pid_file, 'r+') as fp:
                pids = fp.readlines()
                for pid in pids:
                    kill_pid(int(pid.strip()))
                fp.truncate(0)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Plan-text → list[list[tuple]] conversion
# ---------------------------------------------------------------------------

# Recognised values of ``plans[*].format`` produced by
# ``run_planner._infer_plan_format``.
_FORMAT_SEQUENTIAL = "sequential"
_FORMAT_NUMBERED = "numbered-sequential"
_FORMAT_PARALLEL = "parallel-step"
_FORMAT_TEMPORAL = "temporal"

# Regexes shared across formats.
_RE_FF_STEP   = re.compile(r"^step\s+\d+\s*:\s*(.+)$", re.IGNORECASE)
_RE_NUMBERED  = re.compile(r"^\d+(?:\.\d+)?\s*:\s*(.+)$")
_RE_PARENS    = re.compile(r"^\((.*)\)\s*$")
_RE_TEMPORAL  = re.compile(r"^[\d.]+\s*:\s*\((.*?)\)\s*(?:\[[^\]]*\])?\s*$")
_RE_PSTEP     = re.compile(r"^STEP\s+(\d+)(?:\.\d+)?\s*:\s*(.+)$", re.IGNORECASE)
_RE_CALLSITE  = re.compile(r"^([A-Za-z_][\w\-]*)\s*\((.*)\)\s*$")
_RE_PSTEP_LIT = re.compile(r"\(([^()]*)\)")


def _tokenize_action_body(body: str) -> tuple[str, ...] | None:
    """Convert the textual body of an action call into a lowercase tuple.

    Accepted shapes::

        "ACTION ARG ARG"            -> ("action", "arg", "arg")
        "(action arg arg)"          -> ("action", "arg", "arg")
        "action(arg1, arg2)"        -> ("action", "arg1", "arg2")
        "action()" / "action"       -> ("action",)
    """
    body = body.strip()
    if not body:
        return None
    # Strip surrounding parens once.
    m = _RE_PARENS.match(body)
    if m:
        body = m.group(1).strip()
    # function-call shape "name(arg, arg)"
    m = _RE_CALLSITE.match(body)
    if m:
        name = m.group(1)
        args_str = m.group(2)
        tokens = [name] + [a for a in re.split(r"[,\s]+", args_str) if a]
    else:
        tokens = body.split()
    if not tokens:
        return None
    return tuple(t.lower() for t in tokens)


def _parse_one_step(line: str, fmt: str) -> tuple[str, ...] | None:
    """Convert a single action line (sequential/numbered/temporal) into a tuple."""
    m = _RE_FF_STEP.match(line)
    if m:
        return _tokenize_action_body(m.group(1))
    if fmt == _FORMAT_TEMPORAL:
        m = _RE_TEMPORAL.match(line)
        if m:
            return _tokenize_action_body(m.group(1))
    m = _RE_NUMBERED.match(line)
    if m:
        return _tokenize_action_body(m.group(1))
    return _tokenize_action_body(line)


def _parse_parallel_step(line: str) -> tuple[int, list[tuple[str, ...]]] | None:
    """Parse one ``STEP N: a(...) b(...)`` line from a parallel plan."""
    m = _RE_PSTEP.match(line)
    if not m:
        return None
    step = int(m.group(1))
    rest = m.group(2).strip()
    tuples: list[tuple[str, ...]] = []
    # Two shapes coexist in practice:
    #   "STEP 0: (op a b) (op2 c d)"             -> S-exprs
    #   "STEP 0.1: op(a, b)"                     -> Madagascar function-call
    if "(" in rest:
        # Pull out every parenthesised group, preserve textual prefix.
        parts: list[str] = []
        idx = 0
        while idx < len(rest):
            m2 = _RE_PSTEP_LIT.search(rest, idx)
            if not m2:
                break
            head = rest[idx:m2.start()].strip(" ,")
            inner = m2.group(1).strip()
            if head and not head.startswith("("):
                # Madagascar style "name(args)" -> reshape as "name arg1 arg2"
                inner_tokens = " ".join(t for t in re.split(r"[,\s]+", inner) if t)
                parts.append("{} {}".format(head, inner_tokens))
            else:
                parts.append(inner)
            idx = m2.end()
        for body in parts:
            tup = _tokenize_action_body(body)
            if tup:
                tuples.append(tup)
    else:
        tup = _tokenize_action_body(rest)
        if tup:
            tuples.append(tup)
    return (step, tuples)


def _action_obj_to_tuple(action: dict) -> tuple[str, ...] | None:
    """Convert a ``steps[*].actions[*]`` dict into a lowercase tuple.

    The dict has shape ``{"name": str, "args": [str, ...], "pddl": str,
    "duration": float | None}``. ``name`` + ``args`` are preferred; we
    fall back to parsing ``pddl`` when ``name`` is missing.
    """
    name = action.get("name")
    if name:
        args = action.get("args") or []
        return tuple([str(name).lower()] + [str(a).lower() for a in args])
    pddl = action.get("pddl")
    if pddl:
        return _tokenize_action_body(pddl)
    return None


def _convert_steps(steps: list[dict]) -> list[list[tuple[str, ...]]]:
    """Convert ``plans[*].steps`` into Safe-Planner's plan structure.

    Each step becomes one parallel level (a list of action tuples).
    ``index``, ``start_time`` and ``end_time`` are ignored -- ordering
    follows the array order produced by ``run_planner.py``. Empty
    steps and unparsable actions are silently dropped.
    """
    plan: list[list[tuple[str, ...]]] = []
    for step in steps:
        if not isinstance(step, dict):
            continue
        level: list[tuple[str, ...]] = []
        for act in step.get("actions") or []:
            if not isinstance(act, dict):
                continue
            tup = _action_obj_to_tuple(act)
            if tup:
                level.append(tup)
        if level:
            plan.append(level)
    return plan


def _convert_actions(action_lines: list[str], fmt: str) -> list[list[tuple[str, ...]]]:
    """Convert ``plans[*].actions`` into Safe-Planner's plan structure."""
    plan: list[list[tuple[str, ...]]] = []
    if fmt == _FORMAT_PARALLEL:
        buckets: dict[int, list[tuple[str, ...]]] = {}
        for raw in action_lines:
            line = (raw or "").strip()
            if not line or line.startswith(";"):
                continue
            parsed = _parse_parallel_step(line)
            if parsed is None:
                # Best-effort: treat as a standalone sequential step.
                tup = _tokenize_action_body(line)
                if tup:
                    plan.append([tup])
                continue
            step, tuples = parsed
            buckets.setdefault(step, []).extend(tuples)
        for step in sorted(buckets):
            plan.append(buckets[step])
        return plan

    for raw in action_lines:
        line = (raw or "").strip()
        if not line or line.startswith(";"):
            continue
        tup = _parse_one_step(line, fmt)
        if tup:
            plan.append([tup])
    return plan


# ---------------------------------------------------------------------------
# run_planner.py invocation
# ---------------------------------------------------------------------------

_UNSOLVABLE_HINTS = (
    "goal can be simplified to false",
    "problem proven unsolvable",
    "no plan exists",
    "no solution",
    "task is provably unsolvable",
    "unsolvable",
)


def _looks_unsolvable(result: dict) -> bool:
    """Heuristic: does this run_planner result indicate a proven unsolvable task?"""
    rc = result.get("return_code")
    # Fast Downward search exit codes: 11 == unsolvable-incomplete,
    # 12 == unsolvable. ``run_planner`` returns the planner's exit code
    # untouched.
    if rc in (11, 12):
        return True
    blob = ((result.get("stdout") or "")
            + "\n" + (result.get("stderr") or "")).lower()
    return any(hint in blob for hint in _UNSOLVABLE_HINTS)


def _print_detailed_val_report(label: str, validation: dict) -> None:
    """Print the full VAL report for one classical call (``-v 2`` mode).

    Mirrors the layout of ``run_planner.py``'s ``print_validation_report``
    so users see the same detailed diagnostic block they would get when
    running ``run_planner.py`` interactively.
    """
    bar = "=" * 70
    valid = validation.get("valid")
    if valid is True:
        verdict_str = color.fg_yellow("VALID")
    elif valid is False:
        verdict_str = color.fg_red("INVALID")
    else:
        verdict_str = "UNKNOWN"

    print()
    print(color.fg_yellow(bar))
    print(color.fg_yellow("{} -- VAL Plan Validation".format(label)))
    print(color.fg_yellow(bar))
    if not validation.get("available", True) and validation.get("valid") is None:
        print("Status:     SKIPPED")
        if validation.get("error"):
            print("Reason:     {}".format(validation["error"]))
        print(color.fg_yellow(bar))
        return
    if validation.get("command"):
        print("Command:    {}".format(validation["command"]))
    if validation.get("plan_file"):
        print("Plan file:  {}".format(validation["plan_file"]))
    if validation.get("runtime") is not None:
        print("Runtime:    {:.3f}s".format(validation["runtime"]))
    if validation.get("return_code") is not None:
        print("Exit code:  {}".format(validation["return_code"]))
    print("Result:     {}".format(verdict_str))
    if validation.get("error"):
        print("Error:      {}".format(validation["error"]))
    stdout = (validation.get("stdout") or "").strip()
    stderr = (validation.get("stderr") or "").strip()
    if stdout:
        print("\n--- VAL stdout ---")
        print(stdout)
    if stderr:
        print("\n--- VAL stderr ---")
        print(stderr)
    print(color.fg_yellow(bar))


def _build_cmd(planner: str, domain: str, problem: str, out_file: str) -> list[str]:
    yaml_name = _YAML_ALIASES.get(planner, planner)
    profile = profiles.default_name(planner) or "default"
    cmd = [
        sys.executable, str(_RUN_PLANNER),
        str(domain), str(problem),
        "-p", yaml_name,
        "-P", profile,
        "-t", str(DEFAULT_TIMEOUT),
        "-q",                 # capture planner stdout/stderr (no live stream)
        "-o", out_file,       # full result (incl. stdout/stderr) as JSON
    ]
    if VAL_CONFIG.enabled:
        cmd.append("-V")
        cmd.extend(["--val-timeout", str(VAL_CONFIG.timeout)])
        if VAL_CONFIG.epsilon is not None:
            cmd.extend(["--val-epsilon", str(VAL_CONFIG.epsilon)])
        if VAL_CONFIG.verbose:
            cmd.append("--val-verbose")
    return cmd


def call_run_planner(planner: str, domain: str, problem: str, pwd: str, verbose=False):
    """Invoke ``run_planner.py`` for ``planner`` and return a Safe-Planner plan.

    Return value semantics (preserved from the legacy adapters)::

        list[list[tuple]]  -> plan found
        []                 -> trivially solved (planner reported success, no actions)
        None               -> proven unsolvable
        -1                 -> error (binary missing, crash, JSON parse failure, ...)
    """
    canonical = registry.canonical_name(planner) or planner

    # Stage the JSON output file in a per-call tmp path.
    tmp_dir = Path(tempfile.gettempdir()) / "safe-planner-runplanner"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    out_file = str(tmp_dir / "result-{}-{}.json".format(canonical, uuid.uuid4().hex))

    cmd = _build_cmd(canonical, domain, problem, out_file)

    if verbose:
        print(color.fg_yellow("\n>> run_planner: ") + " ".join(cmd))

    pid_file = os.path.join(pwd, "{}-pid.txt".format(canonical))

    # ``start_new_session=True`` puts the child in its own process group so
    # that ``kill_jobs`` (which uses ``killpg``) can terminate the whole
    # planner subtree at once.
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
    except OSError as exc:
        if verbose:
            print(color.fg_red("[run_planner failed to start: {}]".format(exc)))
        return -1

    try:
        with open(pid_file, "a") as fp:
            fp.write("{}\n".format(proc.pid))
    except OSError:
        pass

    try:
        stdout_b, stderr_b = proc.communicate()
    except Exception as exc:
        try:
            proc.kill()
        except Exception:
            pass
        if verbose:
            print(color.fg_red("[run_planner crashed: {}]".format(exc)))
        return -1

    # Load full result (includes stdout/stderr/plans).
    try:
        with open(out_file) as fp:
            result = json.load(fp)
    except (OSError, json.JSONDecodeError) as exc:
        if verbose >= 1:
            print(color.fg_red("[run_planner: cannot read {}: {}]".format(out_file, exc)))
            if stderr_b:
                sys.stderr.write(stderr_b.decode(errors="replace"))
        return -1
    finally:
        try:
            # keep on disk when SAFE_PLANNER_KEEP_RUNPLANNER_JSON is set
            import os as _os
            if not _os.environ.get("SAFE_PLANNER_KEEP_RUNPLANNER_JSON"):
                os.remove(out_file)
            else:
                print(color.fg_yellow("[run_planner JSON kept: ") + out_file + "]")
        except OSError:
            pass

    if verbose >= 2:
        # Surface the captured planner stdout so users can still inspect it.
        sys.stdout.write(result.get("stdout", "") or "")
        sys.stderr.write(result.get("stderr", "") or "")

    # VAL summary embedded in the JSON. ``run_planner.py`` stores VAL output
    # under a ``validation`` dict whose ``valid`` field is
    # ``True`` / ``False`` / ``None`` (``None`` = couldn't run, e.g. empty plan).
    #
    # In default verbosity we print a one-line summary; with ``-v 2`` we
    # surface the full detailed report (command, runtime, exit code, stdout,
    # stderr) -- the same content ``run_planner.py`` would have printed to
    # the terminal in interactive mode.
    if VAL_CONFIG.enabled:
        val = result.get("validation")
        if isinstance(val, dict):
            label = "VAL[{}]".format(canonical)
            if verbose >= 2:
                _print_detailed_val_report(label, val)
            else:
                valid = val.get("valid")
                if valid is True:
                    print(color.fg_yellow(label + ": ") + "valid")
                elif valid is False:
                    err = val.get("error") or "invalid"
                    print(color.fg_red(label + ": invalid -- " + str(err)))
                else:
                    err = val.get("error") or "unknown"
                    print(color.fg_yellow(label + ": ") + "skipped (" + str(err) + ")")

    success = bool(result.get("success"))
    plans = result.get("plans") or []

    if not success and not plans:
        if _looks_unsolvable(result):
            return None
        return -1

    if not plans:
        # success but no plan -- goal already entailed by initial state.
        return []

    selected = next((p for p in plans if p.get("is_selected")), plans[0])

    # Prefer the structured ``steps`` array (introduced in pddl-solvers
    # commit 5c75935): each step is one parallel level holding one or more
    # action objects. Falls back to legacy ``actions`` text parsing for
    # older planner outputs that omit ``steps``.
    steps = selected.get("steps")
    if steps:
        converted = _convert_steps(steps)
        if not converted:
            if verbose:
                print(color.fg_red(
                    "[run_planner: could not parse 'steps' field]"))
            return -1
        return converted

    actions = selected.get("actions") or []
    fmt = selected.get("format") or _FORMAT_SEQUENTIAL

    if not actions:
        return []

    converted = _convert_actions(actions, fmt)
    if not converted and actions:
        # Parsing failed for every line -> treat as error so the caller knows.
        if verbose:
            print(color.fg_red(
                "[run_planner: could not parse plan (format={})]".format(fmt)))
            for ln in actions:
                print(color.fg_red("    " + repr(ln)))
        return -1
    return converted


# ---------------------------------------------------------------------------
# Public dispatcher (single- and multi-processing entry points)
# ---------------------------------------------------------------------------

def Plan(planners, domain, problem, pwd, verbose=False):
    '''Race several planners; return the first plan a planner produces.

    A single planner short-circuits the multiprocessing machinery.
    '''
    try:
        if len(set(planners)) == 1:
            planner = list(planners)[0]
            plan = call_run_planner(planner, domain, problem, pwd, verbose)
            if plan == -1:
                if not verbose:
                    print(color.fg_red("[some error by external planner -- run again with '-v 2']"))
                sys.exit(0)
            return plan

        returned_plan = Queue()
        failed_planners = Array('I', len(planners))
        process_lst = []

        for planner in planners:
            proc = Process(
                target=_mp_worker,
                args=(planner, domain, problem, pwd, returned_plan, failed_planners, verbose),
            )
            proc.daemon = True
            process_lst.append(proc)
            proc.start()

        while returned_plan.empty():
            if sum(failed_planners) == len(planners):
                print(color.fg_red("[error by all external planners: run with '-v 2']"))
                sys.exit(0)

        kill_jobs(pwd, planners)

        while process_lst:
            proc = process_lst.pop()
            while proc.is_alive():
                try:
                    proc.terminate()
                    proc.join()
                except Exception:
                    pass

        return returned_plan.get()
    except KeyboardInterrupt:
        if len(planners) > 1:
            kill_jobs(pwd, planners)
            print(color.bg_red('ALL JOBS TERMINATED'))
        raise


def _mp_worker(planner, domain, problem, pwd, returned_plan, failed_planners, verbose):
    """Multiprocessing worker: run a planner, push the plan or record failure."""
    plan = call_run_planner(planner, domain, problem, pwd, verbose)
    if plan != -1:
        returned_plan.put(plan)
    else:
        try:
            failed_planners[sum(failed_planners)] = 1
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Back-compat shim: a couple of older tests / scripts called these directly.
# ---------------------------------------------------------------------------

def call_planner_sp(planner, domain, problem, args, pwd, verbose):  # noqa: D401
    """Deprecated: kept for backwards compatibility. ``args`` is ignored."""
    return call_run_planner(planner, domain, problem, pwd, verbose)


def call_planner_mp(planner, domain, problem, args, pwd, returned_plan, failed_planners, verbose):  # noqa: D401
    """Deprecated: kept for backwards compatibility. ``args`` is ignored."""
    return _mp_worker(planner, domain, problem, pwd, returned_plan, failed_planners, verbose)

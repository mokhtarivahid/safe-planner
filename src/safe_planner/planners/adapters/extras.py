"""Adapters for the additional planners shipped by pddl-solvers.

Each ``call_*`` function follows the same signature used by the existing
``call_ff`` / ``call_fd`` helpers in :mod:`safe_planner.planners.runner` and
returns one of:

* a non-empty ``list`` — the parsed plan, in the internal Safe-Planner format
  ``[[(action, *args)], ...]``,
* ``None`` — the problem was proven unsolvable by the planner,
* ``-1``   — the planner did not produce a usable plan (error/unsupported
  PDDL/timeout/missing binary).

For planners that do not consistently build out of the box on every machine
the adapter still issues the command via the registry; if the binary is
missing it returns ``-1`` with an informative message instead of crashing.
"""

from __future__ import annotations

import os
import re
import subprocess
import tempfile

from .. import registry
from ... import color


# ----------------------------------------------------------------------------- helpers
def _to_str(output):
    if output is None:
        return ""
    if isinstance(output, bytes):
        return output.decode("utf-8", errors="replace")
    return str(output)


def _exe_or_fail(name, verbose=0):
    """Return a command prefix for ``name`` or ``None`` (after a notice)."""
    cmd = registry.planner_command_prefix(name)
    if cmd is None and verbose:
        print(color.fg_yellow("-- " + registry.describe_missing(name)))
    return cmd


def _run(cmd, pwd, pid_name, verbose=0):
    """Run ``cmd`` capturing stdout/stderr; record PID for cleanup."""
    full = "timeout 1800 {cmd} & echo $! >> {pwd}/{pid}-pid.txt".format(
        cmd=cmd, pwd=pwd, pid=pid_name
    )
    proc = subprocess.Popen(full, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, shell=True,
                            preexec_fn=os.setsid)
    out, err = proc.communicate()
    rc = proc.wait()
    out_s, err_s = _to_str(out), _to_str(err)
    if verbose == 2:
        print(color.fg_voilet("\n-- planner stdout"))
        print(out_s)
        if err_s:
            print(color.fg_voilet("-- planner stderr"))
            print(err_s)
    return rc, out_s, err_s


_ACTION_LINE = re.compile(r"^\s*(?:\d+[:.\)]\s*)?\(\s*([^()]+?)\s*\)\s*(?:;.*)?$")


def _parse_plan_lines(text):
    """Extract ``(action arg1 arg2 ...)`` lines from a block of text.

    Returns a list of single-action steps, suitable for the internal plan
    format ``[[(action, *args)], ...]``. Returns ``[]`` if nothing parses.
    """
    plan = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(";"):
            continue
        m = _ACTION_LINE.match(line)
        if not m:
            continue
        tokens = m.group(1).split()
        if not tokens:
            continue
        plan.append([tuple(tokens)])
    return plan


def _parse_plan_file(path):
    try:
        with open(path) as f:
            return _parse_plan_lines(f.read())
    except FileNotFoundError:
        return []


# ----------------------------------------------------------------------------- FF-family
def _call_ff_like(name, domain, problem, args, pwd, verbose=0,
                  output_flag="-o", problem_flag="-f"):
    """Run an FF-family planner and parse its stdout for a plan."""
    exe = _exe_or_fail(name, verbose)
    if exe is None:
        return -1
    cmd = "{exe} {oflag} {dom} {pflag} {prob} {args}".format(
        exe=exe, oflag=output_flag, dom=domain,
        pflag=problem_flag, prob=problem, args=args,
    )
    rc, out, err = _run(cmd, pwd, name, verbose)
    if rc < 0:
        return -1
    if "problem proven unsolvable" in out.lower() or \
       "no solution" in out.lower() or \
       "goal can be simplified to false" in out.lower():
        return None
    # FF prints its plan after "ff: found legal plan as follows" (or similar)
    plan = _parse_plan_lines(out)
    return plan if plan else -1


def call_metric_ff(domain, problem, args="", pwd="/tmp", verbose=0):
    return _call_ff_like("metric-ff", domain, problem, args, pwd, verbose)


def call_conformant_ff(domain, problem, args="", pwd="/tmp", verbose=0):
    return _call_ff_like("conformant-ff", domain, problem, args, pwd, verbose)


def call_contingent_ff(domain, problem, args="", pwd="/tmp", verbose=0):
    return _call_ff_like("contingent-ff", domain, problem, args, pwd, verbose)


def call_probabilistic_ff(domain, problem, args="", pwd="/tmp", verbose=0):
    return _call_ff_like("probabilistic-ff", domain, problem, args, pwd, verbose)


# ----------------------------------------------------------------------------- Plan-file family
def _call_plan_file_planner(name, build_cmd, pwd, verbose=0, plan_file=None):
    """Common driver for planners that write a plan to a known file."""
    if plan_file is None:
        plan_file = os.path.join(tempfile.gettempdir(), "{}-plan.txt".format(name))
    # let the caller bake plan_file into the cmd
    cmd = build_cmd(plan_file)
    rc, out, err = _run(cmd, pwd, name, verbose)
    if rc < 0:
        return -1
    if "unsolvable" in out.lower() or "no solution" in out.lower():
        return None
    plan = _parse_plan_file(plan_file)
    if not plan:
        # some planners only emit on stdout
        plan = _parse_plan_lines(out)
    return plan if plan else -1


def call_symk(domain, problem, args="", pwd="/tmp", verbose=0):
    """Symbolic-search planner from the pddl-solvers bundle."""
    exe = _exe_or_fail("symk", verbose)
    if exe is None:
        return -1

    def build(plan_file):
        return ("{exe} --search-memory-limit 4G --plan-file {pf} "
                "{dom} {prob} {extra}").format(
            exe=exe, pf=plan_file, dom=domain, prob=problem, extra=args or
            '--search "astar(blind())"'
        )

    return _call_plan_file_planner("symk", build, pwd, verbose)


def call_enhsp(domain, problem, args="", pwd="/tmp", verbose=0):
    """ENHSP numeric/temporal planner."""
    exe = _exe_or_fail("enhsp", verbose)
    if exe is None:
        return -1

    def build(plan_file):
        return "{exe} -o {dom} -f {prob} -sp {pf} {extra}".format(
            exe=exe, dom=domain, prob=problem, pf=plan_file, extra=args
        )

    return _call_plan_file_planner("enhsp", build, pwd, verbose)


def call_popf(domain, problem, args="", pwd="/tmp", verbose=0):
    """POPF temporal planner."""
    exe = _exe_or_fail("popf", verbose)
    if exe is None:
        return -1
    cmd = "{exe} {args} {dom} {prob}".format(
        exe=exe, args=args, dom=domain, prob=problem
    )
    rc, out, err = _run(cmd, pwd, "popf", verbose)
    if rc < 0:
        return -1
    if "problem unsolvable" in out.lower():
        return None
    plan = _parse_plan_lines(out)
    return plan if plan else -1


def call_tfd(domain, problem, args="", pwd="/tmp", verbose=0):
    """Temporal Fast Downward."""
    exe = _exe_or_fail("tfd", verbose)
    if exe is None:
        return -1

    def build(plan_file):
        return "{exe} {dom} {prob} {extra}".format(
            exe=exe, dom=domain, prob=problem, extra=args
        )

    return _call_plan_file_planner("tfd", build, pwd, verbose)


def call_powerlifted(domain, problem, args="", pwd="/tmp", verbose=0):
    """Powerlifted lifted classical planner."""
    exe = _exe_or_fail("powerlifted", verbose)
    if exe is None:
        return -1

    def build(plan_file):
        return ("{exe} --domain {dom} --instance {prob} "
                "--plan-file {pf} {extra}").format(
            exe=exe, dom=domain, prob=problem, pf=plan_file, extra=args
        )

    return _call_plan_file_planner("powerlifted", build, pwd, verbose)


def call_nextflap(domain, problem, args="", pwd="/tmp", verbose=0):
    """NextFLAP temporal planner."""
    exe = _exe_or_fail("nextflap", verbose)
    if exe is None:
        return -1
    cmd = "{exe} -d {dom} -p {prob} {extra}".format(
        exe=exe, dom=domain, prob=problem, extra=args
    )
    rc, out, err = _run(cmd, pwd, "nextflap", verbose)
    if rc < 0:
        return -1
    if "unsolvable" in out.lower():
        return None
    plan = _parse_plan_lines(out)
    return plan if plan else -1

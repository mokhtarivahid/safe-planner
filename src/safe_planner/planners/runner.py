"""Public planner runner with two interchangeable backends.

Two backends are available:

- ``"run_planner"`` *(default)*: every classical call is routed through
  ``third_party/pddl-solvers/run_planner.py``. That script invokes the
  planner binary, picks the matching profile from ``planner_profiles.yaml``
  and -- when ``-V`` is given -- runs VAL itself; we read the JSON it
  writes via ``-o`` and convert the selected plan back into Safe-Planner's
  ``list[list[tuple]]`` format.
- ``"direct"``: per-planner adapters call the planner binaries directly
  (the pre-pddl-solvers behaviour). When ``-V`` is enabled the wrapper in
  :mod:`safe_planner.planners.validation` runs VAL independently after
  every classical call.

The CLI selects the backend with ``--direct`` (off by default). All
callers should use the symbols exported from this module
(``Plan``, ``kill_jobs``, ``VAL_CONFIG``); the two backend modules are
implementation details.
"""

from __future__ import annotations

from . import _direct_backend as _direct
from . import _run_planner_backend as _via_run_planner


# Selected backend: ``"run_planner"`` (default) or ``"direct"``.
BACKEND: str = "run_planner"

# VAL knobs for the *run_planner* backend (forwarded as ``-V --val-*``).
# When ``BACKEND == "direct"`` the CLI mirrors these onto
# :data:`safe_planner.planners.validation.CONFIG` instead.
VAL_CONFIG = _via_run_planner.VAL_CONFIG


def Plan(planners, domain, problem, pwd, verbose=False):
    """Race several planners; return the first plan found.

    Delegates to the currently selected backend.
    """
    if BACKEND == "direct":
        return _direct.Plan(planners, domain, problem, pwd, verbose)
    return _via_run_planner.Plan(planners, domain, problem, pwd, verbose)


def kill_jobs(pwd, planners):
    """Terminate leftover subprocesses recorded by either backend.

    Both backends use the same ``<pwd>/<planner>-pid.txt`` convention so
    we delegate to both (idempotent).
    """
    _via_run_planner.kill_jobs(pwd, planners)
    _direct.kill_jobs(pwd, planners)

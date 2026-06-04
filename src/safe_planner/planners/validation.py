"""Optional VAL plan validation used by the *direct* planner backend.

The default ``run_planner`` backend forwards validation to
``pddl-solvers/run_planner.py`` (which calls VAL itself). When the user
selects the *direct* backend (``--direct``) Safe-Planner calls the planner
binaries directly, so VAL has to be invoked here, once per classical call.

Public API
----------
``CONFIG`` -- :class:`ValidationConfig` populated by the CLI.
``get_val_executable(name)`` -- locate ``Validate``/``Parser``/``ToFn`` in
    ``third_party/pddl-solvers/VAL/build/bin``.
``format_plan_for_val(plan)`` -- turn Safe-Planner's
    ``list[list[tuple]]`` into the line-based plan format VAL expects.
``validate_plan_text(domain, problem, plan_text)`` -- run VAL and return
    ``(valid, summary, stdout, stderr)``.
``validate_plan_if_enabled(planner, domain, problem, plan, verbose)`` --
    one-shot wrapper called by the direct backend after every classical
    call.
``summary_line()`` -- one-line aggregate suitable for the CLI tail.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from .. import color
from . import registry


_VAL_BIN_DIR = registry.REPO_ROOT / "third_party" / "pddl-solvers" / "VAL" / "build" / "bin"


@dataclass
class ValidationConfig:
    enabled: bool = False
    timeout: int = 60
    epsilon: float | None = None
    verbose: bool = False
    # Running aggregates.
    total: int = 0
    valid: int = 0
    invalid: int = 0
    errors: int = 0
    skipped: int = 0


CONFIG = ValidationConfig()


def get_val_executable(name: str = "Validate") -> Path | None:
    """Return the path to a VAL binary inside the pddl-solvers submodule."""
    exe = _VAL_BIN_DIR / name
    return exe if exe.is_file() and os.access(exe, os.X_OK) else None


def format_plan_for_val(plan) -> str:
    """Render Safe-Planner's ``list[list[tuple]]`` in the line format VAL accepts.

    Each step becomes either one ``(action arg ...)`` line (sequential) or
    several lines (one per concurrent action in a parallel step).
    """
    if not plan or plan in (-1, None):
        return ""
    lines: list[str] = []
    for step in plan:
        for action in step:
            if isinstance(action, (list, tuple)):
                lines.append("(" + " ".join(str(t) for t in action) + ")")
            else:
                lines.append(str(action))
    return "\n".join(lines) + ("\n" if lines else "")


def validate_plan_text(domain: str, problem: str, plan_text: str):
    """Invoke ``Validate`` on ``plan_text``. Returns ``(valid, summary, stdout, stderr)``.

    ``valid`` is ``True``/``False``/``None`` (``None`` = couldn't run).
    """
    exe = get_val_executable("Validate")
    if exe is None:
        return None, "VAL Validate binary not found at " + str(_VAL_BIN_DIR), "", ""
    if not plan_text.strip():
        return None, "empty plan", "", ""
    args = [str(exe)]
    if CONFIG.epsilon is not None:
        args.extend(["-t", str(CONFIG.epsilon)])
    if CONFIG.verbose:
        args.append("-v")
    args.extend([domain, problem])
    with tempfile.NamedTemporaryFile("w", suffix=".plan", delete=False) as fp:
        fp.write(plan_text)
        plan_file = fp.name
    args.append(plan_file)
    try:
        proc = subprocess.run(
            args, capture_output=True, text=True, timeout=CONFIG.timeout
        )
    except subprocess.TimeoutExpired:
        return None, "VAL timeout ({}s)".format(CONFIG.timeout), "", ""
    except Exception as exc:
        return None, "VAL subprocess error: {}".format(exc), "", ""
    finally:
        try:
            os.remove(plan_file)
        except OSError:
            pass
    out = proc.stdout or ""
    err = proc.stderr or ""
    if "Plan valid" in out or "Successful plans" in out:
        return True, "valid", out, err
    if "Plan invalid" in out or "validation error" in out.lower():
        return False, "invalid", out, err
    return None, "indeterminate (rc={})".format(proc.returncode), out, err


def validate_plan_if_enabled(planner, domain, problem, plan, verbose=False) -> None:
    """Validate ``plan`` with VAL when :data:`CONFIG.enabled` is ``True``."""
    if not CONFIG.enabled:
        return
    if plan in (-1, None):
        CONFIG.total += 1
        CONFIG.skipped += 1
        return
    plan_text = format_plan_for_val(plan)
    valid, summary, out, err = validate_plan_text(domain, problem, plan_text)
    CONFIG.total += 1
    label = "VAL[{}]".format(planner)
    if valid is True:
        CONFIG.valid += 1
        print(color.fg_yellow(label + ": ") + summary)
    elif valid is False:
        CONFIG.invalid += 1
        print(color.fg_red(label + ": " + summary))
        if verbose:
            if out:
                print(out)
            if err:
                print(err)
    else:
        CONFIG.errors += 1
        print(color.fg_red(label + ": " + summary))
        if verbose and err:
            print(err)


def summary_line() -> str | None:
    """One-line summary of all VAL runs in this Safe-Planner invocation."""
    if not CONFIG.enabled or CONFIG.total == 0:
        return None
    return color.fg_yellow(
        "VAL: {t} validated, {v} valid, {i} invalid, {e} errors, {s} skipped".format(
            t=CONFIG.total, v=CONFIG.valid, i=CONFIG.invalid,
            e=CONFIG.errors, s=CONFIG.skipped,
        )
    )

"""Discovery and resolution of external classical planner executables.

Planners are resolved from a single location:

``third_party/pddl-solvers/planners/<name>/<exe>`` — the canonical source,
added to the project as a git submodule
(https://github.com/mokhtarivahid/pddl-solvers). The binaries are compiled
locally via ``cd third_party/pddl-solvers && ./build_all.sh``.

The registry is intentionally a plain dict so it is trivial to add a new
planner: append an entry to :data:`PLANNERS` describing the candidate
executable paths to look for.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

# Repository root is two parents above this file
# (.../src/safe_planner/planners/registry.py -> .../safe-planner)
REPO_ROOT = Path(__file__).resolve().parents[3]
PDDL_SOLVERS_ROOT = REPO_ROOT / "third_party" / "pddl-solvers" / "planners"


@dataclass(frozen=True)
class PlannerEntry:
    """Describes how to locate a classical planner executable."""

    name: str
    # Candidate paths relative to ``PDDL_SOLVERS_ROOT``.
    pddl_solvers_paths: tuple[str, ...] = ()
    # Friendly description.
    description: str = ""
    # Whether to run via "python3 <path>" instead of "./<path>".
    python_script: bool = False
    # Whether the executable is a Java JAR (run via "java -jar <path>").
    java_jar: bool = False
    # Aliases that resolve to this planner (CLI/back-compat).
    aliases: tuple[str, ...] = field(default_factory=tuple)


PLANNERS: dict[str, PlannerEntry] = {
    # ---- FF family ------------------------------------------------------
    "ff": PlannerEntry(
        name="ff",
        pddl_solvers_paths=("ff/ff",),
        description="Fast-Forward (FF) classical planner.",
    ),
    "ff-x": PlannerEntry(
        name="ff-x",
        pddl_solvers_paths=("ff-x/ff",),
        description="FF with PDDL 2.1 derived predicates (axioms).",
    ),
    "metric-ff": PlannerEntry(
        name="metric-ff",
        pddl_solvers_paths=("metric-ff/ff",),
        description="FF for numeric PDDL 2.1 (level 2) planning.",
    ),
    "conformant-ff": PlannerEntry(
        name="conformant-ff",
        # Conformant-FF's makefile produces a binary named ``ff``.
        pddl_solvers_paths=("conformant-ff/ff",),
        description="FF for conformant planning under initial-state uncertainty.",
    ),
    "contingent-ff": PlannerEntry(
        name="contingent-ff",
        # Contingent-FF's makefile produces a binary named ``ff``.
        pddl_solvers_paths=("contingent-ff/ff",),
        description="FF for contingent planning with sensing actions.",
    ),
    "probabilistic-ff": PlannerEntry(
        name="probabilistic-ff",
        pddl_solvers_paths=("probabilistic-ff/ff",),
        description="FF for probabilistic planning with Bayesian initial states.",
    ),
    # ---- Modern planners -----------------------------------------------
    "fd": PlannerEntry(
        name="fd",
        pddl_solvers_paths=("downward/fast-downward.py",),
        description="Fast-Downward classical planner.",
        python_script=True,
        aliases=("fast-downward", "downward"),
    ),
    "symk": PlannerEntry(
        name="symk",
        pddl_solvers_paths=("symk/fast-downward.py",),
        description="SymK — optimal / top-k symbolic planner.",
        python_script=True,
    ),
    "enhsp": PlannerEntry(
        name="enhsp",
        # ENHSP ships as a Java JAR; it is invoked via ``java -jar``.
        pddl_solvers_paths=("enhsp/enhsp.jar", "enhsp/enhsp-dist/enhsp.jar"),
        description="ENHSP — Numeric planning (also classical).",
        java_jar=True,
    ),
    # ---- Temporal planners ---------------------------------------------
    "optic-clp": PlannerEntry(
        name="optic-clp",
        # OPTIC's CMake build places the binary under build/src/optic/.
        pddl_solvers_paths=(
            "optic/build/src/optic/optic-clp",
            "optic/build/optic-clp",
            "optic/optic-clp",
        ),
        description="OPTIC (CLP backend) — Temporal planner.",
        aliases=("optic",),
    ),
    "popf": PlannerEntry(
        name="popf",
        pddl_solvers_paths=("popf/build/popf", "popf/popf"),
        description="POPF — Partial-order temporal planner.",
        aliases=("popf3-clp",),
    ),
    "tfd": PlannerEntry(
        name="tfd",
        # ``downward/tfd`` is the expected wrapper; ``downward/search/search``
        # is the underlying search binary produced by the build.
        pddl_solvers_paths=(
            "tfd/downward/tfd",
            "tfd/downward/search/search",
        ),
        description="Temporal Fast-Downward.",
    ),
    # ---- Other classical/lifted ----------------------------------------
    "lpg": PlannerEntry(
        name="lpg",
        pddl_solvers_paths=("lpg/lpg",),
        description="LPG — local-search planner.",
    ),
    "lpg-td": PlannerEntry(
        name="lpg-td",
        # pddl-solvers builds the temporal/derived-predicate variant as
        # ``lpg-probing`` (via ``./configure -probing``). Fall back to plain
        # ``lpg`` for older builds.
        pddl_solvers_paths=("lpg/lpg-probing", "lpg/lpg-td", "lpg/lpg"),
        description="LPG-td — temporal/derived-predicate variant of LPG.",
    ),
    "vhpop": PlannerEntry(
        name="vhpop",
        # Some builds install the IPC-3 wrapper under ``ipc3-vhpop``.
        pddl_solvers_paths=("vhpop/vhpop", "vhpop/ipc3-vhpop"),
        description="VHPOP — partial-order planner.",
    ),
    "madagascar": PlannerEntry(
        name="madagascar",
        pddl_solvers_paths=("madagascar/M", "madagascar/Mp", "madagascar/MpC"),
        description="MADAGASCAR — SAT-based planner.",
        aliases=("m",),
    ),
    "powerlifted": PlannerEntry(
        name="powerlifted",
        pddl_solvers_paths=("powerlifted/powerlifted.py",),
        description="PowerLifted — lifted planning for large object domains.",
        python_script=True,
    ),
    "nextflap": PlannerEntry(
        name="nextflap",
        pddl_solvers_paths=("nextflap/nextflap",),
        description="NextFLAP — expressive hybrid planner.",
    ),
}


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------

def _resolve_alias(name: str) -> str:
    """Map any alias or case variant to the canonical planner key."""
    key = name.lower()
    if key in PLANNERS:
        return key
    for canonical, entry in PLANNERS.items():
        if key in (a.lower() for a in entry.aliases):
            return canonical
    return key  # unknown — caller will get None from resolve_executable


def available_planners() -> list[str]:
    """Return the canonical planner names known to Safe-Planner."""
    return sorted(PLANNERS)


def cli_choices() -> list[str]:
    """Return canonical names plus aliases — suitable as argparse choices."""
    names = set(PLANNERS)
    for entry in PLANNERS.values():
        names.update(entry.aliases)
    return sorted(names)


def canonical_name(name: str) -> str:
    """Public wrapper around alias resolution."""
    return _resolve_alias(name)


def _first_existing(roots: Iterable[Path], candidates: Iterable[str]) -> Path | None:
    for root in roots:
        for rel in candidates:
            path = root / rel
            if path.is_file():
                return path
    return None


def resolve_executable(name: str) -> Path | None:
    """Resolve a planner name to a concrete executable path on disk.

    Returns ``None`` if no executable could be located under
    ``third_party/pddl-solvers``.
    """
    key = _resolve_alias(name)
    entry = PLANNERS.get(key)
    if entry is None:
        return None
    return _first_existing([PDDL_SOLVERS_ROOT], entry.pddl_solvers_paths)


def planner_runner_prefix(entry: PlannerEntry, exe: Path) -> str:
    """Build the leading command fragment for an executable.

    ``python3 <script>`` for python scripts (Fast-Downward, SymK,
    PowerLifted...), ``java -jar <jar>`` for Java JAR planners (ENHSP),
    ``<exe>`` for native binaries.
    """
    if entry.python_script:
        return f"python3 {exe}"
    if entry.java_jar:
        return f"java -jar {exe}"
    return str(exe)


def planner_entry(name: str) -> PlannerEntry | None:
    """Look up an entry by name or alias."""
    return PLANNERS.get(_resolve_alias(name))


def executable_in_dir(name: str, basename: str) -> Path | None:
    """Return ``<planner-dir>/<basename>`` if it exists for ``name``.

    This is used to honour per-configuration executable overrides declared in
    pddl-solvers' ``planner_configurations.yaml`` (e.g. Madagascar's
    ``Mp`` / ``MpC`` / ``M`` binaries, or LPG's ``lpg-probing`` variant).
    """
    entry = planner_entry(name)
    if entry is None:
        return None
    for rel in entry.pddl_solvers_paths:
        candidate = PDDL_SOLVERS_ROOT / Path(rel).parent / basename
        if candidate.is_file():
            return candidate
    return None


def planner_command_prefix(name: str) -> str | None:
    """Resolve ``name`` to a ready-to-exec command prefix, or ``None``."""
    entry = planner_entry(name)
    if entry is None:
        return None
    exe = resolve_executable(name)
    if exe is None:
        return None
    return planner_runner_prefix(entry, exe)


# Convenience for CLI help and error messages
def describe_missing(name: str) -> str:
    """Human-readable message explaining where Safe-Planner looked."""
    entry = planner_entry(name)
    if entry is None:
        return f"Unknown planner '{name}'. Known: {', '.join(available_planners())}"
    looked = [str(PDDL_SOLVERS_ROOT / rel) for rel in entry.pddl_solvers_paths]
    bullets = "\n  - ".join(looked) if looked else "(no known locations)"
    return (
        f"Planner '{name}' executable not found. Looked in:\n  - {bullets}\n"
        f"Build pddl-solvers with:\n"
        f"  cd {os.path.relpath(REPO_ROOT / 'third_party' / 'pddl-solvers')} "
        f"&& ./build_all.sh --planner {entry.name}"
    )

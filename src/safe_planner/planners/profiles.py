"""Adapter between Safe-Planner and the pddl-solvers profile catalogue.

pddl-solvers ships a YAML file
(:file:`third_party/pddl-solvers/planner_profiles.yaml`) that describes
each planner together with one or more named *profiles*. A profile carries
either an ``args`` list (CLI flags) or a ``search`` expression (for
search-driven planners like Fast-Downward, SymK and ENHSP), plus an
optional ``executable`` override (used by Madagascar to switch between its
``M`` / ``Mp`` / ``MpC`` binaries, and by LPG to switch between ``lpg`` and
``lpg-probing``).

This module wraps :class:`PlannerProfiles` from pddl-solvers and exposes a
:data:`profiles` singleton with :meth:`Profiles.resolve` /
:meth:`Profiles.args` helpers. Each planner has a single *active* profile;
that profile is the YAML entry named ``default`` (when present) or the
first entry of the planner's YAML ``profiles`` block, and can be
overridden at runtime via :meth:`Profiles.set_default` (driven by the
CLI's ``--profile`` flag) or compile-time via
:data:`_DEFAULT_PROFILE_OVERRIDES`.

When the pddl-solvers submodule (or PyYAML) is not available, the module
falls back to a small built-in mirror of the profiles that used to live
inline in :mod:`safe_planner.planners.runner`. That guarantees the project
still runs even before ``git submodule update --init`` is executed.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from . import registry

# ---------------------------------------------------------------------------
# YAML loader (lazy + optional dependency)
# ---------------------------------------------------------------------------

_PDDL_SOLVERS_REPO = registry.REPO_ROOT / "third_party" / "pddl-solvers"
_PROFILES_YAML = _PDDL_SOLVERS_REPO / "planner_profiles.yaml"
# Legacy filename kept around for users that haven't pulled the rename yet.
_LEGACY_CONFIG_YAML = _PDDL_SOLVERS_REPO / "planner_configurations.yaml"


def _load_pddl_solvers_spec():
    """Return the parsed YAML spec, or ``None`` if unavailable."""
    yaml_path = _PROFILES_YAML if _PROFILES_YAML.is_file() else _LEGACY_CONFIG_YAML
    if not yaml_path.is_file():
        return None
    # Prefer the upstream loader so we get the exact same parsing semantics.
    if str(_PDDL_SOLVERS_REPO) not in sys.path:
        sys.path.insert(0, str(_PDDL_SOLVERS_REPO))
    # New module name first; fall back to the legacy class for older checkouts.
    try:
        from planner_profiles import PlannerProfiles  # type: ignore
        return PlannerProfiles(str(yaml_path))
    except Exception:
        try:
            from planner_configurations import PlannerConfigurations  # type: ignore
            return _LegacySpecAdapter(PlannerConfigurations(str(yaml_path)))
        except Exception:
            # Fallback to a direct YAML read if PyYAML is installed.
            try:
                import yaml  # type: ignore
            except ImportError:
                return None
            with open(yaml_path) as f:
                data = yaml.safe_load(f) or {}
            return _MiniSpec(data)


class _MiniSpec:
    """Minimal stand-in mimicking the bits of ``PlannerProfiles`` we use."""

    def __init__(self, data: Mapping[str, Any]) -> None:
        self._planners = (data or {}).get("planners", {})

    def has_planner(self, name: str) -> bool:
        return name in self._planners

    def get_profiles(self, name: str) -> dict:
        info = self._planners.get(name, {})
        # New schema uses ``profiles``; legacy used ``configurations``.
        return info.get("profiles") or info.get("configurations", {})

    def get_planner_executable(self, name: str) -> str:
        return self._planners.get(name, {}).get("executable", name)


class _LegacySpecAdapter:
    """Adapter that exposes the new ``get_profiles`` name on legacy specs."""

    def __init__(self, legacy_spec) -> None:
        self._spec = legacy_spec

    def has_planner(self, name: str) -> bool:
        return self._spec.has_planner(name)

    def get_profiles(self, name: str) -> dict:
        return self._spec.get_configurations(name)

    def get_planner_executable(self, name: str) -> str:
        return self._spec.get_planner_executable(name)


# ---------------------------------------------------------------------------
# Per-planner wrappers that turn YAML "search" / "args" into a CLI fragment
# ---------------------------------------------------------------------------

def _wrap_search_fd(expr: str) -> str:
    return '--search "{}"'.format(expr)


def _wrap_search_symk(expr: str) -> str:
    return '--search "{}"'.format(expr)


def _wrap_search_enhsp(expr: str) -> str:
    # ENHSP uses a "-planner <preset>" alias for built-in search recipes; if the
    # config supplies an explicit command (with spaces), keep it verbatim
    # under the same flag.
    return '-planner {}'.format(expr)


# Mapping of planner -> function that turns a YAML "search" string into the
# CLI fragment expected by the corresponding ``call_*`` function in
# :mod:`safe_planner.planners.runner`.
_SEARCH_WRAPPERS = {
    "fd": _wrap_search_fd,
    "downward": _wrap_search_fd,
    "symk": _wrap_search_symk,
    "enhsp": _wrap_search_enhsp,
}


# When a planner name has no entry in the YAML we fall back to this mapping.
# Keys mirror the names used by Safe-Planner's registry / dispatcher.
_FALLBACK_PROFILES: dict[str, dict[str, dict[str, Any]]] = {
    "lpg-td": {
        "default":  {"args": ["-speed", "-noout"]},
        "quality":  {"args": ["-quality", "-v", "off", "-noout"]},
    },
    # Conservative compiled-in defaults that match the original Safe-Planner
    # behaviour for the planners that *are* in the YAML — used only if the
    # submodule is not initialised.
    "ff":          {"default": {"args": []}},
    "ff-x":        {"default": {"args": []}},
    "metric-ff":   {"default": {"args": []}},
    "conformant-ff":    {"default": {"args": []}},
    "contingent-ff":    {"default": {"args": []}},
    "probabilistic-ff": {"default": {"args": []}},
    "madagascar":  {"default": {"args": ["-P", "1", "-N", "-m", "4096"]}},
    "optic-clp":   {"default": {"args": ["-N"]}},
    "popf":        {"default": {"args": []}},
    "tfd":         {"default": {"args": []}},
    "vhpop": {"default": {"args": ["-g", "-f", "DSep-LIFO", "-s", "HC",
                                    "-w", "5", "-l", "1500000"]}},
    "lpg":         {"default": {"args": ["-n", "1", "-noout"]}},
    "fd": {"default": {"search": ("lazy_greedy([ff()], preferred=[ff()])")}},
    "symk":        {"default": {"search": "astar(blind())"}},
    "enhsp":       {"default": {"search": "sat-hmrp"}},
    "powerlifted": {"default": {"args": ["-s", "gbfs", "-e", "ff"]}},
    "nextflap":    {"default": {"args": []}},
}


# Mapping from Safe-Planner's canonical planner name to the key used inside
# pddl-solvers' ``planner_configurations.yaml`` (when they differ).
_YAML_ALIASES: dict[str, str] = {
    "fd": "downward",
    "optic-clp": "optic",
    "lpg-td": "lpg",
}


# Per-planner remap of the default profile. Use this only when the YAML's
# default entry is unsuitable for Safe-Planner's FOND replanning loop.
# Override at runtime with ``--profile PLANNER:NAME``. Currently empty:
# every planner uses the ``default`` profile declared in
# ``pddl-solvers/planner_profiles.yaml`` (e.g. Fast-Downward's
# ``astar(lmcut())`` optimal default).
_DEFAULT_PROFILE_OVERRIDES: dict[str, str] = {}
# Backwards-compatible alias for callers that still import the old name.
_DEFAULT_CONFIG_OVERRIDES = _DEFAULT_PROFILE_OVERRIDES


# Per-planner whitelist of profile names that support axioms / derived
# predicates. Used by :meth:`Profiles.ensure_axiom_safe` when the planning
# domain contains ``:derived`` definitions. The first listed entry is the
# preferred fall-back. Fast-Downward heuristics ``ff``/``add`` support
# axioms; ``lmcut``/``cea``/``cg`` do not (which is why the YAML default
# ``astar(lmcut())`` cannot handle them).
_AXIOM_SAFE_PROFILES: dict[str, tuple[str, ...]] = {
    "fd": ("optimal-ff", "satisficing-ff"),
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ResolvedConfig:
    """A configuration resolved to ready-to-run command pieces."""

    name: str
    args: str
    executable_basename: str | None = None


class Profiles:
    """Loader/resolver for pddl-solvers planner profiles."""

    def __init__(self) -> None:
        self._spec = _load_pddl_solvers_spec()
        # per-process overrides set via CLI ``--profile PLANNER:NAME``
        self._runtime_default: dict[str, str] = {}

    def set_default(self, planner: str, name: str) -> int:
        """Override the default profile for ``planner``.

        Returns the index of ``name`` in the planner's profile list so the
        caller can verify the mapping. Raises :class:`KeyError` if the
        planner has no profiles, or :class:`ValueError` if ``name`` is not
        among them.
        """
        canonical = registry.canonical_name(planner)
        names = self.list_configs(canonical)
        if not names:
            raise KeyError("planner '{}' has no known profiles".format(planner))
        if name not in names:
            raise ValueError(
                "profile '{}' not in [{}]".format(name, ", ".join(names))
            )
        self._runtime_default[canonical] = name
        return names.index(name)

    # -- introspection -----------------------------------------------------
    def _yaml_name(self, planner: str) -> str:
        return _YAML_ALIASES.get(planner, planner)

    def _yaml_configs(self, planner: str) -> dict:
        spec = self._spec
        yaml_name = self._yaml_name(planner)
        if spec is None or not spec.has_planner(yaml_name):
            return {}
        # Preserve insertion order.
        return dict(spec.get_profiles(yaml_name))

    def _fallback_configs(self, planner: str) -> dict:
        return _FALLBACK_PROFILES.get(planner, {})

    def list_configs(self, planner: str) -> list[str]:
        """Ordered list of config names; ``[]`` for unknown planners."""
        canonical = registry.canonical_name(planner)
        configs = self._yaml_configs(canonical) or self._fallback_configs(canonical)
        return list(configs.keys())

    def configs(self, planner: str) -> dict:
        """Ordered ``{name: config_dict}`` mapping for ``planner``."""
        canonical = registry.canonical_name(planner)
        return self._yaml_configs(canonical) or self._fallback_configs(canonical)

    def default_name(self, planner: str) -> str | None:
        """Name of the profile used when no override is in effect."""
        canonical = registry.canonical_name(planner)
        if canonical in self._runtime_default:
            return self._runtime_default[canonical]
        if canonical in _DEFAULT_PROFILE_OVERRIDES:
            return _DEFAULT_PROFILE_OVERRIDES[canonical]
        names = self.list_configs(canonical)
        if not names:
            return None
        # New YAML schema uses an explicit ``default`` key when present.
        return "default" if "default" in names else names[0]

    # -- resolution --------------------------------------------------------
    def _select(self, planner: str) -> tuple[str, dict]:
        """Return ``(name, config_dict)`` for ``planner``'s active profile."""
        configs = self._yaml_configs(planner) or self._fallback_configs(planner)
        if not configs:
            return ("default", {"args": []})
        if planner in self._runtime_default:
            preferred = self._runtime_default[planner]
            if preferred in configs:
                return (preferred, configs[preferred])
        if planner in _DEFAULT_PROFILE_OVERRIDES:
            preferred = _DEFAULT_PROFILE_OVERRIDES[planner]
            if preferred in configs:
                return (preferred, configs[preferred])
        # Prefer the explicit ``default`` profile when present (new schema).
        if "default" in configs:
            return ("default", configs["default"])
        name = next(iter(configs))
        return (name, configs[name])

    def resolve(self, planner: str) -> ResolvedConfig:
        """Return a :class:`ResolvedConfig` for ``planner``'s active profile."""
        canonical = registry.canonical_name(planner)
        name, cfg = self._select(canonical)

        # Build the args fragment.
        if "search" in cfg:
            wrapper = _SEARCH_WRAPPERS.get(canonical, lambda s: s)
            args_str = wrapper(cfg["search"])
        else:
            args_list = cfg.get("args", []) or []
            args_str = " ".join(str(a) for a in args_list)

        return ResolvedConfig(
            name=name,
            args=args_str,
            executable_basename=cfg.get("executable"),
        )

    def args(self, planner: str) -> str:
        """Convenience: return just the args fragment for the active profile."""
        return self.resolve(planner).args

    def ensure_axiom_safe(self, planner: str) -> str | None:
        """Ensure ``planner``'s active profile supports derived predicates.

        If the user already pinned an axiom-safe profile via
        :meth:`set_default` it is kept untouched. Otherwise the first entry
        from :data:`_AXIOM_SAFE_PROFILES` that exists in the catalogue is
        installed as the runtime default.

        Returns the name of the profile that ends up active, or ``None``
        if no axiom-safe profile is known for ``planner`` (in which case
        the caller should warn the user).
        """
        canonical = registry.canonical_name(planner)
        candidates = _AXIOM_SAFE_PROFILES.get(canonical, ())
        if not candidates:
            return None
        available = self.configs(canonical)
        # Respect an explicit --profile if it is already axiom-safe.
        current = self._runtime_default.get(canonical)
        if current and current in candidates:
            return current
        for name in candidates:
            if name in available:
                # set_default validates membership and records the override.
                self.set_default(canonical, name)
                return name
        return None

    # -- back-compat helpers ----------------------------------------------
    def describe(self, planner: str) -> str:
        names = self.list_configs(planner)
        if not names:
            return "<no profiles known for '{}'>".format(planner)
        return ", ".join(names)


# Module-level singleton.
profiles = Profiles()

"""Safe-Planner: A FOND planner that compiles non-deterministic PPDDL
problems into classical planning problems and merges classical plans into
a strong-cyclic policy.

Public re-exports for embedding Safe-Planner in other Python code.
"""

from .planner import Planner  # noqa: F401

__version__ = "0.3.0"
__all__ = ["Planner", "__version__"]

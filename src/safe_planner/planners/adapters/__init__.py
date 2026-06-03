"""Per-planner adapter modules.

Each adapter exposes a `call(domain, problem, args, pwd, verbose)` function
that returns a plan in the Safe-Planner internal format
(`list[list[tuple[str, ...]]]`), or `None` for unsolvable, or `-1` on error.
"""

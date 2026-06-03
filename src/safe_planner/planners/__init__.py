"""External classical-planner adapters and dispatcher.

`runner.py` keeps the multiprocessing dispatcher and the original adapters
(ff, fd, m, optic-clp, vhpop, lpg, lpg-td).  The `adapters/` package
contains additional adapters for the planners that ship with the
`pddl-solvers` submodule (symk, enhsp, popf, tfd, ...).
"""

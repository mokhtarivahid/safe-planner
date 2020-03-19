#!/usr/bin/env python3

import argparse

from color import fg_green, fg_red, fg_yellow, fg_blue, fg_voilet, fg_beige, bg_voilet, bg_beige
from planner import Planner


def parse():
    usage = 'python3 main.py <DOMAIN> <PROBLEM> [<PLANNER>] [-v | --verbose N] [-h | --help]'
    description = "Safe-Planner is a non-deterministic planner for PPDDL."
    parser = argparse.ArgumentParser(usage=usage, description=description)

    parser.add_argument('domain',  type=str, help='path to PDDL domain file')
    parser.add_argument('problem', type=str, help='path to PDDL problem file')
    parser.add_argument("planner", type=str, nargs='?', const=1, 
        help="external planner: ff, m, optic, vhpop, ... (default=ff)", default="ff")
    # parser.add_argument("-v", "--verbose", help="increase output verbosity", 
    #     action="store_true")
    parser.add_argument("-v", "--verbose", default=0, type=int, 
        help="increase output verbosity: 0 (nothing), 1 (high-level), 2 (external planners outputs) (default=0)", )

    return parser.parse_args()


if __name__ == '__main__':

    args = parse()

    ## make a policy given domain and problem
    policy = Planner(args.domain, args.problem, args.planner, args.verbose)

    ## transform the produced policy into a contingency plan
    plan = policy.plan(args.verbose)

    ## print out the plan in a readable form
    policy.print_plan(plan, verbose=args.verbose, del_effects_included=True)

    ## print out sub-paths in the plan
    if args.verbose: policy.print_paths(plan=plan, del_effects_included=True, verbose=args.verbose)

    print('Planning time: %.3f s' % policy.planning_time)
    print('Total number of replannings: %i' % policy.planning_call)
    print('Total number of calls to unsolvable states: %i' % policy.unsolvable_call)

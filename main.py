#!/usr/bin/env python3

import argparse
import os

# from color import fg_green, fg_red, fg_yellow, fg_blue, fg_voilet, fg_beige, bg_voilet, bg_beige
from color import *
from planner import Planner
from dot_plan import gen_dot_plan
from json_plan import gen_json_plan

def main(**args):
  pass

def parse():
    usage = 'python3 main.py <DOMAIN> <PROBLEM> [-x <PLANNER>] [-p] [-d] [-j] [-v N] [-h]'
    description = "Safe-Planner is a non-deterministic planner for PPDDL."
    parser = argparse.ArgumentParser(usage=usage, description=description)

    parser.add_argument('domain',  nargs='?', type=str, help='path to a PDDL domain file')
    parser.add_argument('problem', nargs='?', type=str, help='path to a PDDL problem file')
    parser.add_argument("-x", "--explanner", type=str, default="ff", choices=os.listdir('planners'),
        help="external planner: ff, m, optic-clp, lpg-td, vhpop, ... (default=ff)")
    # parser.add_argument("-v", "--verbose", help="increase output verbosity", 
    #     action="store_true")
    parser.add_argument("-p", "--path", help="print out possible paths of the produced policy", 
        action="store_true")
    parser.add_argument("-d", "--dot", help="draw a graph of the produced policy into a dot file", 
        action="store_true")
    # parser.add_argument("-t", "--tree", help="include goal states as individual steps (combine with \'-d\' to see the difference in the produced dot file)", 
    #     action="store_true")
    parser.add_argument("-j", "--json", help="transform the produced policy into a json file", 
        action="store_true")
    parser.add_argument("-v", "--verbose", default=0, type=int, choices=(0, 1, 2),
        help="increase output verbosity: 0 (nothing), 1 (high-level), 2 (external planners outputs) (default=0)", )

    return parser.parse_args()


if __name__ == '__main__':

    args = parse()

    ## make a policy given domain and problem
    policy = Planner(args.domain, args.problem, args.explanner, args.verbose)

    ## transform the produced policy into a contingency plan
    # plan = policy.plan(tree=args.tree, verbose=args.verbose)
    plan = policy.plan(verbose=args.verbose)

    ## print out the plan in a readable form
    policy.print_plan(plan, del_effects_included=True, verbose=args.verbose)

    ## print out sub-paths in the plan
    if args.path: 
        paths = policy.get_paths(plan, verbose=args.verbose)
        policy.print_paths(paths=paths, del_effects_included=True, verbose=args.verbose)
        # for path in paths:
        #     policy.print_plan(plan=path, del_effects_included=True, verbose=args.verbose)
        ## generate graphs of sub-paths too
        if args.dot:
            for i, path in enumerate(paths):
                dot_file = gen_dot_plan(plan=path)
                print(fg_yellow('-- path{} dot file: ').format(str(i+1)) + dot_file)
                # os.system('xdot %s &' % dot_file)
            print('')

    ## generate a graph of the policy as a dot file in graphviz
    if args.dot:
        plan = policy.plan(tree=True, verbose=args.verbose)
        dot_file = gen_dot_plan(plan=plan, dot_file=args.problem)
        print(fg_yellow('-- dot file: ') + dot_file + '\n')
        os.system('xdot %s &' % dot_file)
        # if not args.tree: 
        #     print(fg_beige('-- try also \'-d\' with \'-t\' to generate a tree-like plan dot file\n'))

    ## transform the policy into a json file
    if args.json:
        json_file, plan_json = gen_json_plan(plan, args.problem)
        # print(fg_yellow('-- json plan object\n') + str(plan_json))
        print(fg_yellow('-- json file: ') + json_file + fg_red(' [EXPERIMENTAL!]\n'))

    print('Planning time: %.3f s' % policy.planning_time)
    print('Total number of replannings: %i' % policy.planning_call)
    print('Total number of calls to unsolvable states: %i' % policy.unsolvable_call)

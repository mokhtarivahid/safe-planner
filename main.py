#!/usr/bin/env python

import argparse
import os, sys, traceback

import color
import planner
import dot_plan

# set the limit of stack
sys.setrecursionlimit(20000)


def parse():
    usage = 'python3 main.py <DOMAIN> <PROBLEM> [-c <PLANNERS>] [-r] [-a] [-p] [-d] [-j] [-s] [-v N] [-h]'
    description = "Safe-Planner is a non-deterministic planner for PPDDL."
    parser = argparse.ArgumentParser(usage=usage, description=description)

    parser.add_argument('domain',  nargs='?', type=str, help='path to a PDDL domain file')
    parser.add_argument('problem', nargs='?', type=str, help='path to a PDDL problem file')
    parser.add_argument("-c", "--planners", nargs='+', type=str, default=["ff"], 
        choices=os.listdir('planners'), metavar='PLNNER', 
        help="a list of classical planners: ff, fd, m, optic-clp, lpg-td, lpg, vhpop (e.g. -c ff fd m) (default=[ff])")
    parser.add_argument("-r", "--rank", help="if '-r' not given, the compiled classical planning domains \
        are ranked by the number of effects in Ascending order; and if '-r' given, in Descending order \
        (default=Ascending)", action="store_true", default=False)
    parser.add_argument("-a", "--all-outcome", help="by default the planner uses both single-outcome and all-outcome \
        compilation strategies; given '-a' it uses only all-outcome strategy to compile from \
        non-deterministic to classical planning domains (default=False)", action="store_true", default=False)
    parser.add_argument("-sp", "--safe-planner", help="switch to the (unsound) SP algorithm (default=NDP2)", 
        action="store_true", default=False)
    parser.add_argument("-d", "--dot", help="draw a graph of the produced policy into a dot file", 
        action="store_true")
    parser.add_argument("-p", "--path", help="print out possible paths of the produced policy", 
        action="store_true")
    parser.add_argument("-j", "--json", help="transform the produced policy into a json file", 
        action="store_true")
    parser.add_argument("-s", "--store", help="store the planner's performance in a '.stat' file", 
        action="store_true")
    parser.add_argument("-v", "--verbose", default=0, type=int, choices=(0, 1, 2),
        help="increase output verbosity: 0 (minimal), 1 (high-level), 2 (classical planners outputs) (default=0)", )

    return parser


def main():
    ## parse arguments
    parser = parse()
    args = parser.parse_args()
    if args.domain == None:
        parser.print_help()
        sys.exit()

    ## make a policy given domain and problem
    policy = planner.Planner(args.domain, args.problem, args.planners, args.safe_planner, args.rank, args.all_outcome, args.verbose)

    ## transform the produced policy into a contingency plan
    plan = policy.plan()

    ## print out the plan in a readable form
    policy.print_plan(del_effect_inc=True, det_effect_inc=False)

    ## print out sub-paths in the plan
    if args.path: 
        paths = policy.get_paths(plan)
        policy.print_paths(paths=paths, del_effect_inc=True)
        # for path in paths:
        #     policy.print_plan(plan=path, del_effect_inc=True)
        ## generate graphs of sub-paths too
        if args.dot:
            for i, path in enumerate(paths):
                dot_file = dot_plan.gen_dot_plan(plan=path)
                print(color.fg_yellow('-- path{} dot file: ').format(str(i+1)) + dot_file)
                # os.system('xdot %s &' % dot_file)
            dot_file = dot_plan.gen_dot_plan(plan=paths[0])
            # os.system('xdot %s &' % dot_file)
            print('')

    ## generate a graph of the policy as a dot file in graphviz
    if args.dot:
        plan = policy.plan(tree=True)
        dot_file = dot_plan.gen_dot_plan(plan=plan, del_effect=True, domain_file=args.domain, problem_file=args.problem)
        print(color.fg_yellow('-- dot file: ') + dot_file + '\n')
        # os.system('xdot %s &' % dot_file)
        # os.system('dot -T pdf %s > %s.pdf &' % (dot_file, dot_file))
        # os.system('evince %s.pdf &' % dot_file)

    ## transform the policy into a json file
    if args.json:
        import json_ma_plan 
        import dot_ma_plan 
        json_output = json_ma_plan.json_ma_plan(policy, verbose=args.verbose)
        if json_output is not None: 
            plan_json_file, actions_json_file = json_output
            print(color.fg_yellow('-- plan_json_file:') + plan_json_file + color.fg_red(' [EXPERIMENTAL!]'))
            print(color.fg_yellow('-- actions_json_file:') + actions_json_file + color.fg_red(' [EXPERIMENTAL!]'))
            os.system('cd lua && lua json_multiagent_plan.lua ../%s &' % plan_json_file)
            print(color.fg_yellow('-- plan_json_dot_file:') + ('%s.dot' % plan_json_file) + color.fg_red(' [EXPERIMENTAL!]'))
            # transform the plan into a parallel plan
            dot_file, tred_dot_file = dot_ma_plan.parallel_plan(policy, verbose=args.verbose)
            print(color.fg_yellow('-- graphviz file: ') + dot_file)
            print(color.fg_yellow('-- transitive reduction: ') + tred_dot_file)
            # os.system('xdot %s.dot &' % plan_json_file)

    ## transform the policy into a json file
    if args.json:
        import json_plan
        plan = policy.plan(tree=False)
        json_file, plan_json = json_plan.json_plan(policy)
        print(color.fg_yellow('\n-- json file: ') + json_file + color.fg_red(' [EXPERIMENTAL!]'))
        print(color.fg_yellow('-- try: ') + 'lua json_plan.lua ' + json_file + color.fg_red(' [EXPERIMENTAL!]\n'))

    if args.store:
        stat_file = policy.log_performance(plan)
        print(color.fg_yellow('-- planner performance: ') + stat_file)

    # print out resulting info
    if args.problem is not None: 
        print('\nPlanning domain: %s' % policy.domain_file)
        print('Planning problem: %s' % policy.problem_file)
        print('Arguments: %s' % ' '.join(sys.argv[3:]))
    else: 
        print('Planning problem: %s' % policy.domain_file)
        print('Arguments: %s' % ' '.join(sys.argv[2:]))
    print('Policy length: %i' % len(policy.policy))
    print('Plan length: %i' % (len(plan)-1))
    print('Compilation time: %.3f s' % policy.compilation_time)
    print('Planning time: %.3f s' % policy.planning_time)
    print('Planning iterations (all-outcome): %i' % policy.alloutcome_planning_call)
    print('Total number of replannings (single-outcome): %i' % policy.singleoutcome_planning_call)
    print('Total number of unsolvable states: %i' % len(policy.unsolvable_states))


if __name__ == '__main__':
    main()
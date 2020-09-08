#!/usr/bin/env python3

import argparse
import os, sys, traceback
import subprocess
import signal

# from color import fg_green, fg_red, fg_yellow, fg_blue, fg_voilet, fg_beige, bg_voilet, bg_beige
from color import *
from planner import Planner
from dot_plan import gen_dot_plan
from json_ma_plan import json_ma_plan
from json_plan import json_plan

# set the limit of stack
sys.setrecursionlimit(20000)

# make sure all running planners are terminated at exit
def cleanup(signum, frame):
    # print("Execution inside '{0}', "
    #       "with local namespace: {1}"
    #        .format(frame.f_code.co_name, frame.f_locals.keys()))
    try:
        # print('got a signal %d' % signum)
        if signum != signal.SIGTERM or\
           signum != signal.SIGINT:
            from external_planner import pid_lst, kill_pid
            # kill the running planners if any
            for i, pid in enumerate(pid_lst):
                pid_lst[i] = kill_pid(pid)
    except OSError:
        # traceback.print_exc()
        pass
    finally:
        sys.exit(0)

# signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)


def parse():
    usage = 'python3 main.py <DOMAIN> <PROBLEM> [-c <PLANNERS>] [-r] [-p] [-d] [-j] [-s] [-v N] [-h]'
    description = "Safe-Planner is a non-deterministic planner for PPDDL."
    parser = argparse.ArgumentParser(usage=usage, description=description)

    parser.add_argument('domain',  nargs='?', type=str, help='path to a PDDL domain file')
    parser.add_argument('problem', nargs='?', type=str, help='path to a PDDL problem file')
    parser.add_argument("-c", "--planners", nargs='*', type=str, default=["ff"], #choices=os.listdir('planners'),
        help="a list of external classical planners: ff, fd, m, optic-clp, lpg-td, vhpop, ... (default=[ff])")
    parser.add_argument("-r", "--rank", help="to disable ranking the compiled classical planning domains \
        by higher probabilistic outcomes (default=True)", action="store_true", default=False)
    parser.add_argument("-p", "--path", help="print out possible paths of the produced policy", 
        action="store_true")
    parser.add_argument("-d", "--dot", help="draw a graph of the produced policy into a dot file", 
        action="store_true")
    parser.add_argument("-j", "--json", help="transform the produced policy into a json file", 
        action="store_true")
    parser.add_argument("-s", "--store", help="store the planner's performance in a '.stat' file", 
        action="store_true")
    parser.add_argument("-v", "--verbose", default=0, type=int, choices=(0, 1, 2),
        help="increase output verbosity: 0 (minimal), 1 (high-level), 2 (external planners outputs) (default=0)", )

    return parser


if __name__ == '__main__':

    ## parse arguments
    parser = parse()
    args = parser.parse_args()
    if args.domain == None:
        parser.print_help()
        sys.exit()

    ## make a policy given domain and problem
    policy = Planner(args.domain, args.problem, args.planners, args.rank, args.verbose)

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
                dot_file = gen_dot_plan(plan=path)
                print(fg_yellow('-- path{} dot file: ').format(str(i+1)) + dot_file)
                # os.system('xdot %s &' % dot_file)
            dot_file = gen_dot_plan(plan=paths[0])
            # subprocess.Popen(["xdot", dot_file])
            # os.system('xdot %s &' % dot_file)
            print('')

    ## generate a graph of the policy as a dot file in graphviz
    if args.dot:
        plan = policy.plan(tree=True)
        dot_file = gen_dot_plan(plan=plan, del_effect=True, dot_file=args.problem)
        print(fg_yellow('-- dot file: ') + dot_file + '\n')
        # subprocess.Popen(["xdot", dot_file])
        # os.system('xdot %s &' % dot_file)
        # os.system('dot -T pdf %s > %s.pdf &' % (dot_file, dot_file))
        # os.system('evince %s.pdf &' % dot_file)

    ## transform the policy into a json file
    if args.json:
        from dot_ma_plan import parallel_plan
        plan_json_file, actions_json_file = json_ma_plan(policy, verbose=args.verbose)
        print(fg_yellow('-- plan_json_file:') + plan_json_file + fg_red(' [EXPERIMENTAL!]'))
        print(fg_yellow('-- actions_json_file:') + actions_json_file + fg_red(' [EXPERIMENTAL!]'))
        os.system('cd lua && lua json_multiagent_plan.lua ../%s &' % plan_json_file)
        print(fg_yellow('-- plan_json_dot_file:') + ('%s.dot' % plan_json_file) + fg_red(' [EXPERIMENTAL!]'))
        # transform the plan into a parallel plan
        dot_file, tred_dot_file = parallel_plan(policy, verbose=args.verbose)
        print(fg_yellow('-- graphviz file: ') + dot_file)
        print(fg_yellow('-- transitive reduction: ') + tred_dot_file)
        # subprocess.Popen(["xdot", plan_json_file])
        # os.system('xdot %s.dot &' % plan_json_file)

    ## transform the policy into a json file
    if args.json:
        plan = policy.plan(tree=False)
        json_file, plan_json = json_plan(policy)
        print(fg_yellow('\n-- json file: ') + json_file + fg_red(' [EXPERIMENTAL!]'))
        print(fg_yellow('-- try: ') + 'lua json_plan.lua ' + json_file + fg_red(' [EXPERIMENTAL!]\n'))

    if args.store:
        stat_file = policy.log_performance(plan)
        print(fg_yellow('-- planner performance: ') + stat_file)

    print('\nPlanning domain: %s' % policy.domain_file)
    print('Planning problem: %s' % policy.problem_file)
    print('Policy length: %i' % len(policy.policy))
    print('Planning time: %.3f s' % policy.planning_time)
    print('Planning iterations (all-outcome): %i' % policy.alloutcome_planning_call)
    print('Total number of replannings (single-outcome): %i' % policy.singleoutcome_planning_call)
    print('Total number of unsolvable states: %i' % len(policy.unsolvable_states))

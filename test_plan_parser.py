#!/usr/bin/env python3

import argparse

from color import fg_green, fg_red, fg_yellow, fg_blue, fg_voilet, fg_beige, bg_voilet, bg_beige
from planner import Planner


def parse():
    usage = 'python3 main.py <DOMAIN> <PROBLEM> [<PLANNER>] [-v | --verbose]'
    description = "pyppddl is a probabilistic planner."
    parser = argparse.ArgumentParser(usage=usage, description=description)

    parser.add_argument('domain',  type=str, help='path to PDDL domain file')
    parser.add_argument('problem', type=str, help='path to PDDL problem file')
    parser.add_argument("planner", type=str, nargs='?', const=1, 
        help="external planner: ff, m, optic, vhpop, ... (default=ff)", default="ff")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", 
        action="store_true")

    return parser.parse_args()



###############################################################################
def parse_plan(plan):

    # a sample code to parse the output plan
    for level, step in plan.items():
        print('@ level ' + level)
        if step == 'goal':
            # goal state is achieved
            print(fg_voilet('@ goal'))
            pass
        elif step == None:
            # normally shouldn't happen; otherwise, something is wrong (report it if happened)
            # anyway, it makes the plan a weak solution
            print(bg_voilet('None!'))
            pass
        else:
            # unfold step into a tuple of actoins and outcomes
            (actions, outcomes) = step
            # execute action at each step and produce the results
            for action in actions:
                # you can access to the properties of the action:
                print(fg_yellow('>> action: ') + action.sig)
                print(fg_yellow('   preconditions:' ) + action.preconditions)
                print(fg_yellow('   effects: ') + action.add_effects)
                pass
            # each outcome is a tuple of conditions and jump to a next level
            # check the outcome of the actions for jumping to the next step
            for (conditions, jump) in outcomes:
                # unfold conditions as add and delete lists
                if len(conditions) > 0: 
                    (add_list, del_list) = conditions
                    # check if the conditions meet in the current state
                    if add_list: print(fg_yellow('   effect+: ') + ' '.join(map(str,add_list)))
                    if del_list: print(fg_yellow('   effect-: ') + ' '.join(map(str,del_list)))
                # jump to the next step if the conditions met
                print(fg_beige('   jump to: ') + jump)
                pass
###############################################################################


if __name__ == '__main__':

    args = parse()

    policy = Planner(args.domain, args.problem, args.planner, args.verbose)

    plan = policy.plan()
    parse_plan(plan)

    print()
    policy.print_plan()

    print('Planning time: %.3f s' % policy.planning_time)
    print('Number of replannings:', policy.planning_call)


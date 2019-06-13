
import argparse
from color import fg_green, fg_red, fg_yellow, fg_blue, fg_voilet, fg_beige

from planner import Planner


def parse():
    usage = 'python3 main.py <DOMAIN> <PROBLEM> [<PLANNER>] [-v | --verbose]'
    description = "pypddl is a probabilistic planner."
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
        print(fg_beige('@@ level'), level)
        if step == 'goal':
            # goal state is achieved
            print(fg_voilet('@ goal'))
            pass
        else:
            # unfold step into a tuple of actoins and outcomes
            (actions, outcomes) = step
            # execute action at each step and produce the results
            for action in actions:
                # you can access to the properties of the action:
                print(fg_yellow('>> action:'), action.sig)
                print(fg_yellow('preconditions:'), action.preconditions)
                print(fg_yellow('add_effects:'), action.add_effects)
                print(fg_yellow('del_effects:'), action.del_effects)
                pass
            # each outcome is a tuple of conditions and jump to a next level
            # check the outcome of the actions for jumping to the next step
            for (conditions, jump) in outcomes:
                # check if the conditions meet in the current state
                print(fg_yellow('condition:'), ' '.join(map(str,conditions)))
                # jump to the next step if the conditions met
                print(fg_yellow('jump to:'), jump)
                pass
###############################################################################


if __name__ == '__main__':

    args = parse()

    policy = Planner(args.domain, args.problem, args.planner, args.verbose)

    plan = policy.plan()

    policy.print_plan(plan)

    parse_plan(plan)

#!/usr/bin/env python3

import argparse
import os, time

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


###############################################################################
def gen_dot_plan(plan, dot_file=None):

    dot_str = str()
    dot_str+= 'digraph Struc {\n'
    dot_str+= ' graph [fontname = "helvetica"];\n'
    dot_str+= ' node [fontname = "helvetica"];\n'
    dot_str+= ' edge [fontname = "helvetica"];\n'
    dot_str+= ' node [shape=ellipse];\n'
    dot_str+= ' packMode="graph";\n'

    # a sample code to parse the output plan
    for level, step in plan.items():
        if step == 'GOAL':
            # goal state is achieved
            dot_str+= ' n{} [shape=circle,label="",peripheries=2];\n'.format(str(level))
            pass
        elif step == None:
            # normally shouldn't happen; unless, something went wrong (report it if happened)
            # anyway, it makes the plan a weak solution
            dot_str+= ' n{} [shape=circle,label="",peripheries=1];\n'.format(str(level))
            pass
        else:
            # unfold step into a tuple of actions and outcomes
            (actions, outcomes) = step
            dot_str+= ' n{} [label="{}"];\n'.format(str(level), ' '.join(map(str, actions)))

            # each outcome is a tuple of conditions and jump to a next level
            for (conditions, jump) in outcomes:
                # unfold conditions as add and delete lists
                (add_list, del_list) = ([],[])
                if len(conditions) > 0: (add_list, del_list) = conditions
                add_str = '+ {}'.format(str(' '.join(map(str,[str('('+' '.join(eff)+')') for eff in add_list]))))\
                            if add_list else ''
                del_str = '\\n- {}'.format(str(' '.join(map(str,[str('('+' '.join(eff)+')') for eff in del_list]))))\
                            if del_list else ''
                dot_str+= ' n{}->n{} [label="{}{}"];\n'.format(str(level), str(jump), (add_str), (del_str))
                # dot_str+= ' n{}->n{} [label=" + {}\\n- {} "];\n'.format(str(level), str(jump), \
                #     str(' '.join(map(str,[str('('+' '.join(eff)+')') for eff in add_list]))), \
                #     str(' '.join(map(str,[str('('+' '.join(eff)+')') for eff in del_list]))))
    dot_str+= '}'

    # create a dot file
    if dot_file == None:
        if not os.path.exists("/tmp/pyddl/"):
            os.makedirs("/tmp/pyddl/")
        dot_file = "/tmp/pyddl/prob"+str(int(time.time()*1000000))+".dot"
    else:
        dot_file = '{}.dot'.format(os.path.splitext(os.path.abspath(dot_file))[0])
    with open(dot_file, 'w') as f:
        f.write(dot_str)
        f.close()
    return dot_file


###############################################################################
if __name__ == '__main__':

    args = parse()

    policy = Planner(args.domain, args.problem, args.planner, args.verbose)

    plan = policy.plan()
    policy.print_plan(plan)

    dot_file = gen_dot_plan(plan=plan, dot_file=args.problem)
    print(dot_file)

    print('Planning time: %.3f s' % policy.planning_time)
    print('Total number of replannings: %i' % policy.planning_call)
    print('Total number of calls to unsolvable states: %i' % policy.unsolvable_call)

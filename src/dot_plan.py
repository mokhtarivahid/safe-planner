#!/usr/bin/env python

import argparse
import os, time

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
def gen_dot_plan(plan, del_effect=True, domain_file=None, problem_file=None):

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
            continue
        elif step == None:
            # normally should not happen; unless, something went wrong
            # anyway, it makes the plan a weak solution
            dot_str+= ' n{} [shape=circle,label="",peripheries=1];\n'.format(str(level))
        else:
            # unfold step into a tuple of actions and outcomes
            (actions, outcomes) = step
            # create a node for the current step
            if len(outcomes) > 1: 
                # non-deterministic step in different color
                dot_str+= ' n{} [style=filled, color=lightgrey, label="{}"];\n'.format(str(level), ' '.join(map(str, actions)))
            else:
                # deterministic step
                dot_str+= ' n{} [label="{}"];\n'.format(str(level), ' '.join(map(str, actions)))

            # each outcome is a tuple of conditions and jump to a next level
            for (conditions, jump) in outcomes:
                # unfold conditions as add and delete lists
                (add_list, del_list) = ([],[])

                # if action is non-deterministic (has some effects)
                if len(conditions) > 0: (add_list, del_list) = conditions

                # create an edge and its label
                eff_str = '+ {}'.format(str(' '.join(map(str,[str('('+' '.join(eff)+')') for eff in add_list]))))\
                            if add_list else ''
                if del_effect:
                    eff_str+= '\\n- {}'.format(str(' '.join(map(str,[str('('+' '.join(eff)+')') for eff in del_list]))))\
                            if del_list else ''
                dot_str+= ' n{}->n{} [fontsize=12, label="{}"];\n'.format(str(level), str(jump), (eff_str))
                # check if goal is achieved at the next step
                # if jump == 'GOAL': dot_str+= ' n{} [shape=circle,label="",peripheries=2];\n'.format(str(jump))
    dot_str+= '}'

    # create a dot file
    if problem_file is not None:
        problem_file = '{}.dot'.format(os.path.splitext(problem_file)[0])
    elif domain_file is not None:
        problem_file = '{}.dot'.format(os.path.splitext(domain_file)[0])
    else:
        if not os.path.exists("/tmp/safe-planner/"):
            os.makedirs("/tmp/safe-planner/")
        problem_file = "/tmp/safe-planner/prob"+str(int(time.time()*1000000))+".dot"

    with open(problem_file, 'w') as f:
        f.write(dot_str)
        f.close()
    return problem_file


###############################################################################
if __name__ == '__main__':

    import planner 

    args = parse()

    policy = planner.Planner(args.domain, args.problem, args.planner, args.verbose)

    plan = policy.plan(tree=True)
    policy.print_plan(plan)

    dot_file = gen_dot_plan(plan=plan, del_effect=False, domain_file=args.domain, problem_file=args.problem)
    print(dot_file)

    print('Planning time: %.3f s' % policy.planning_time)
    print('Total number of replannings: %i' % policy.planning_call)
    print('Total number of calls to unsolvable states: %i' % policy.unsolvable_call)

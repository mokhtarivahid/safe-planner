# [THIS IS AN EXPERIMENTAL VERSION AND ONLY WORKS FOR DETERMINISTIC PLANS!]
# transforms a plan into a multi-agent plan and generates two json files 
# for plan and actions descriptions

# requirement:
# pip install pygraphviz

#!/usr/bin/env python3

import argparse
from collections import defaultdict
import os, time
from pygraphviz import *

# from color import fg_green, fg_red, fg_yellow, fg_blue, fg_voilet, fg_beige, bg_voilet, bg_beige
from color import *
from planner import Planner
from domain import Action

def parse():
    usage = 'python3 main.py <DOMAIN> <PROBLEM> [<PLANNER>] [-d] [-v] [-h]'
    description = "Safe-Planner is a non-deterministic planner for PPDDL."
    parser = argparse.ArgumentParser(usage=usage, description=description)

    parser.add_argument('domain',  type=str, help='path to a PDDL domain file')
    parser.add_argument('problem', type=str, help='path to a PDDL problem file')
    parser.add_argument("-c", "--planners", nargs='*', type=str, default=["ff"], #choices=os.listdir('planners'),
        help="a list of external classical planners: ff, fd, m, optic-clp, lpg-td, vhpop, ... (default=[ff])")
    parser.add_argument("-r", "--rank", help="to disable ranking the compiled classical planning domains \
        by higher probabilistic outcomes (default=True)", action="store_true", default=False)
    parser.add_argument("-d", "--dot", help="draw a graph of the produced policy into a dot file", 
        action="store_true")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", 
        action="store_true")

    return parser.parse_args()


## a function to convert a list of literals into a pddl string
def literals_to_pddl(literal_lst):

    if len(literal_lst) == 0: return str()

    def literal_to_pddl(literal):
        if literal[0] == -1:
            return '(not ({0}))'.format(' '.join(map(str, literal[1:][0])))
        return '({0})'.format(' '.join(map(str, literal)))

    if len(literal_lst) == 1: return literal_to_pddl(literal_lst[0])
    return '{}'.format(' '.join(map(str, [literal_to_pddl(e) for e in literal_lst])))

#################################################################
def parallel_plan(policy, verbose=False):
    '''
    return a list of sub-plans that can be run in parallel as well as 
    joint_executions between sub-plans
    '''
    plan = policy.plan()

    # create dummy start and end actions for initial and goal states
    end = Action(name='end').ground(('end',))
    start = Action(name='start').ground(('start',))

    #############################
    # store edges of the graph
    edges = defaultdict(set)

    progress_list = [(end, policy.problem.goals)]

    for level, step in reversed(plan.items()):
        if level == 'GOAL' or step == None or step == 'GOAL': continue
        new_progress_list = []
        for (act, goal_lst) in progress_list:
            (actions, outcomes) = step
            for action in actions:
                if len(set(action.effects.add_effects).intersection(set(goal_lst))) > 0:
                    new_progress_list.append( (action, action.preconditions.pos_preconditions) )
                    edges[action].add(act)
                if len(set(action.preconditions.pos_preconditions).intersection(set(act.effects.del_effects))) > 0:
                    edges[action].add(act)
        progress_list = progress_list + new_progress_list

    # add a start node to the beginning actions
    # (actions, outcomes) = plan[0]
    # for action in actions:
    #     edges[start].add(action)

    #############################
    dot_file = '{}.gv'.format(os.path.splitext(policy.problem_file)[0])
    prob_name = os.path.splitext(os.path.basename(policy.problem_file))[0]

    # create a graphviz object
    G = AGraph(directed=True)

    # attributes
    # G.graph_attr['label']=prob_name
    G.node_attr['shape']='ellipse'
    G.node_attr['fontname']='helvetica'
    G.edge_attr['fontname']='helvetica'

    # add edges to the graph
    for tail, heads in edges.items():
        for head in heads:
            pred_lst = list(set(tail.effects.add_effects).intersection(set(head.preconditions.pos_preconditions)))
            if not head.name == 'end' and not pred_lst: pred_lst = tail.effects.add_effects
            G.add_edge('{}'.format(str(tail)), '{}'.format(str(head)), label=literals_to_pddl(pred_lst))

    # write to file
    G.write(dot_file) 
    if verbose: print(G.string())

    # do transitive reduction
    # create a new graph 
    # T = G.tred(copy=True)
    # T.draw('{}.tred.gv'.format(os.path.splitext(args.problem)[0])) 

    # do a transitive reduction
    tred_dot_file = '{}.tred.gv'.format(os.path.splitext(policy.problem_file)[0])
    os.system('tred %s | dot -Tdot > %s &' % (dot_file, tred_dot_file))

    # time.sleep(0.1)
    # create a new graph from file
    # T = AGraph('{}.tred.gv'.format(os.path.splitext(args.problem)[0]))
    # print(T.string())

    return dot_file, tred_dot_file


#################################################################
if __name__ == '__main__':

    args = parse()

    # make a policy given domain and problem
    policy = Planner(args.domain, args.problem, args.planners, args.rank, args.verbose)

    # transform the produced policy into a contingency plan and print it
    plan = policy.plan()
    policy.print_plan(plan=plan)


    #############################
    # transform the plan into a parallel plan
    dot_file, tred_dot_file = parallel_plan(policy, verbose=args.verbose)
    print(fg_yellow('-- graphviz file: ') + dot_file)
    print(fg_yellow('-- transitive reduction: ') + tred_dot_file)

    print('\nPlanning domain: %s' % policy.domain_file)
    print('Planning problem: %s' % policy.problem_file)
    print('Policy length: %i' % len(policy.policy))
    print('Planning time: %.3f s' % policy.planning_time)
    print('Planning iterations (all-outcome): %i' % policy.alloutcome_planning_call)
    print('Total number of replannings (single-outcome): %i' % policy.singleoutcome_planning_call)
    print('Total number of unsolvable states: %i' % len(policy.unsolvable_states))

# [THIS IS AN EXPERIMENTAL VERSION AND ONLY WORKS FOR DETERMINISTIC PLANS!]
# transforms a plan into a multi-agent plan and generates two json files 
# for plan and actions descriptions

# requirement:
# pip install pygraphviz

#!/usr/bin/env python

import argparse
import os, time
from collections import defaultdict
from pygraphviz import *

import domain

def parse_args(dir_path=''):
    usage = 'python3 main.py <DOMAIN> <PROBLEM> [<PLANNER>] [-d] [-v] [-h]'
    description = "Safe-Planner is a non-deterministic planner for PPDDL."
    parser = argparse.ArgumentParser(usage=usage, description=description)

    parser.add_argument('domain',  nargs='?', type=str, help='path to a PDDL domain file')
    parser.add_argument('problem', nargs='?', type=str, help='path to a PDDL problem file')
    parser.add_argument("-c", "--planners", nargs='+', type=str, default=["ff"], 
        choices=os.listdir(os.path.join(dir_path, 'planners')), metavar='PLNNER', 
        help="a list of classical planners: ff, fd, m, prob, optic-clp, lpg-td, lpg, vhpop (e.g. -c ff fd m) (default=[ff])")
    parser.add_argument("-r", "--rank", help="to disable ranking the compiled classical planning domains \
        by higher probabilistic outcomes (default=True)", action="store_true", default=False)
    parser.add_argument("-d", "--dot", help="draw a graph of the produced policy into a dot file", 
        action="store_true")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", 
        action="store_true")

    return parser


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
    end = domain.Action(name='end').ground(('end',))
    start = domain.Action(name='start').ground(('start',))

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
                # also check for oneof_effects
                for oneof_effects in action.oneof_effects:
                    for oneof_effect in oneof_effects:
                        if len(set(oneof_effect.add_effects).intersection(set(goal_lst))) > 0:
                            new_progress_list.append( (action, action.preconditions.pos_preconditions) )
                            edges[action].add(act)
                for oneof_effects in act.oneof_effects:
                    for oneof_effect in oneof_effects:
                        if len(set(action.preconditions.pos_preconditions).intersection(set(oneof_effect.del_effects))) > 0:
                            edges[action].add(act)
                # also check for prob_effects
                for prob_effects in action.prob_effects:
                    for prob_effect in prob_effects:
                        if len(set(prob_effect[1].add_effects).intersection(set(goal_lst))) > 0:
                            new_progress_list.append( (action, action.preconditions.pos_preconditions) )
                            edges[action].add(act)
                for prob_effects in act.prob_effects:
                    for prob_effect in prob_effects:
                        if len(set(action.preconditions.pos_preconditions).intersection(set(prob_effect[1].del_effects))) > 0:
                            edges[action].add(act)

        progress_list = progress_list + new_progress_list

    # # link 'start' to the actions in the first step 
    # for action in next(iter(plan.items()))[1][0]:
    #     edges[start].add(action)

    # link 'start' to all actions whose their preconditions are met in the initial_state 
    for level, step in reversed(plan.items()):
        if level == 'GOAL' or step == None or step == 'GOAL': continue
        (actions, outcomes) = step
        for action in actions:
            if len(set(action.preconditions.pos_preconditions).intersection(set(policy.problem.initial_state.predicates))) > 0:
                edges[start].add(action)

    # add a start node to the beginning actions
    # (actions, outcomes) = plan[0]
    # for action in actions:
    #     edges[start].add(action)

    #############################
    problem_file = policy.problem_file
    if problem_file is None:
        problem_file = policy.domain_file
    dot_file = '{}.gv'.format(os.path.splitext(problem_file)[0])
    prob_name = os.path.splitext(os.path.basename(problem_file))[0]

    # create a graphviz object
    G = AGraph(directed=True)

    # attributes
    # G.graph_attr['label']=prob_name
    G.graph_attr['fontname']='helvetica'
    # G.graph_attr['splines']='curved'
    G.node_attr['fontname']='helvetica'
    G.node_attr['shape']='ellipse'
    G.edge_attr['fontname']='helvetica'

    # add edges to the graph
    for tail, heads in edges.items():
        for head in heads:
            pred_lst = list(set(tail.effects.add_effects).intersection(set(head.preconditions.pos_preconditions)))
            for oneof_effects in tail.oneof_effects:
                for oneof_effect in oneof_effects:
                    pred_lst = pred_lst + list(set(oneof_effect.add_effects).intersection(set(head.preconditions.pos_preconditions)))
            for prob_effects in tail.prob_effects:
                for prob_effect in prob_effects:
                    pred_lst = pred_lst + list(set(prob_effect[1].add_effects).intersection(set(head.preconditions.pos_preconditions)))
            if not head.name == 'end' and not pred_lst: pred_lst = tail.effects.add_effects
            G.add_edge('{}'.format(str(tail)), '{}'.format(str(head)), label=literals_to_pddl(pred_lst))
            if head.name in policy.prob_actions:
                G.add_node('{}'.format(str(head)), style='filled', color='lightgrey')

    # update the attributes of start and end nodes
    s = G.get_node('(start)')
    e = G.get_node('(end)')
    s.attr['shape']='circle'
    s.attr['label']="start"
    s.attr['peripheries']=1
    e.attr['shape']='circle'
    e.attr['label']="end"
    e.attr['peripheries']=2

    # write to file
    G.write(dot_file) 
    if verbose: print(G.string())

    # do transitive reduction
    # create a new graph 
    # T = G.tred(copy=True)
    # T.draw('{}.tred.gv'.format(os.path.splitext(args.problem)[0])) 

    # do a transitive reduction
    G.tred()
    tred_dot_file = '{}.tred.gv'.format(os.path.splitext(problem_file)[0])
    G.write(tred_dot_file)
    # os.system('tred %s | dot -Tdot > %s &' % (dot_file, tred_dot_file))

    # time.sleep(0.1)
    # create a new graph from file
    # T = AGraph('{}.tred.gv'.format(os.path.splitext(args.problem)[0]))
    # print(T.string())

    return dot_file, tred_dot_file


#################################################################
if __name__ == '__main__':

    def parse_relative_path():

        # store the input working directory
        cwd = os.getcwd()

        # find the absolute path of 'main.py'
        dir_path = os.path.dirname(os.path.realpath(__file__))

        # find the relative path between 'cwd' and 'dir_path'
        rel_path = os.path.relpath(dir_path,cwd)

        # change working directory to the absolute path of __file__ ('main.py')
        os.chdir(dir_path)

        # parse arguments
        parser = parse_args(dir_path)
        args = parser.parse_args()
        if args.domain == None:
            parser.print_help()
            sys.exit()

        # if the path of the given domain and problem files is absolute
        # update the path of the given domain and problem files
        if not os.path.isabs(args.domain):
            args.domain = os.path.relpath(args.domain,rel_path)

        if not args.problem is None:
            if not os.path.isabs(args.problem): 
                args.problem = os.path.relpath(args.problem,rel_path)

        # a trick when only a problem is passed, the domain is inferred automatically
        # note: there must a 'domain.pddl' file in the same path
        if args.problem is None:
            with open(args.domain) as f:
                data = f.read()
                if not all(x in data for x in ['(problem','(domain']):
                    args.problem = args.domain
                    args.domain = os.path.join( os.path.dirname(args.domain), 'domain.pddl')

        return args

    # parse and refine relative input paths as well as arguments
    args = parse_relative_path()

    import planner
    import color

    # make a policy given domain and problem
    policy = planner.Planner(args.domain, args.problem, args.planners, args.rank, args.verbose)

    # transform the produced policy into a contingency plan and print it
    plan = policy.plan()
    policy.print_plan(plan=plan)


    #############################
    # transform the plan into a parallel plan
    dot_file, tred_dot_file = parallel_plan(policy, verbose=args.verbose)
    print(color.fg_yellow('-- graphviz file: ') + dot_file)
    print(color.fg_yellow('-- transitive reduction: ') + tred_dot_file)

    print('\nPlanning domain: %s' % policy.domain_file)
    print('Planning problem: %s' % policy.problem_file)
    print('Policy length: %i' % len(policy.policy))
    print('Planning time: %.3f s' % policy.planning_time)
    print('Planning iterations (all-outcome): %i' % policy.alloutcome_planning_call)
    print('Total number of replannings (single-outcome): %i' % policy.singleoutcome_planning_call)
    print('Total number of unsolvable states: %i' % len(policy.unsolvable_states))

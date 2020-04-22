#!/usr/bin/env python3

import argparse
from collections import OrderedDict, defaultdict
import os, time
from custom_json import *
from graphviz import Digraph


# from color import fg_green, fg_red, fg_yellow, fg_blue, fg_voilet, fg_beige, bg_voilet, bg_beige
from color import *
from planner import Planner, mergeDict
from dot_plan import gen_dot_plan
from pddl import to_pddl

def parse():
    usage = 'python3 main.py <DOMAIN> <PROBLEM> [<PLANNER>] [-d] [-v] [-h]'
    description = "Safe-Planner is a non-deterministic planner for PPDDL."
    parser = argparse.ArgumentParser(usage=usage, description=description)

    parser.add_argument('domain',  type=str, help='path to a PDDL domain file')
    parser.add_argument('problem', type=str, help='path to a PDDL problem file')
    parser.add_argument("planner", type=str, nargs='?', const=1, 
        help="external planner: ff, m, optic-clp, vhpop, ... (default=ff)", default="ff")
    parser.add_argument("-d", "--dot", help="draw a graph of the produced policy into a dot file", 
        action="store_true")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", 
        action="store_true")

    return parser.parse_args()


#################################################################
def add_effects(action, state, initial_state):
    '''returns all positive effects of @action applicable in @state'''

    # add_lists = set(action.effects.add_effects)
    add_lists = set(action.effects.add_effects)-set(initial_state.predicates)

    ## conditional when effect
    for effect in action.effects.when_effects:
        (pos_cnd_lst, neg_cnd_lst, pos_eff_lst, neg_eff_lst) = effect
        if state.is_true(pos_cnd_lst, neg_cnd_lst):
            # add_lists.update(set(pos_eff_lst))
            add_lists.update(set(pos_eff_lst)-set(initial_state.predicates))

    ## probabilistic effects
    for prob_effect in action.prob_effects:
        for prob in prob_effect:
            # add_lists.update(set(prob[1].add_effects))
            add_lists.update(set(prob[1].add_effects)-set(initial_state.predicates))
            ## conditional when effect
            for effect in prob[1].when_effects:
                (pos_cnd_lst, neg_cnd_lst, pos_eff_lst, neg_eff_lst) = effect
                if state.is_true(pos_cnd_lst, neg_cnd_lst):
                    # add_lists.update(set(pos_eff_lst))
                    add_lists.update(set(pos_eff_lst)-set(initial_state.predicates))

    ## non-deterministic effects
    for oneof_effect in action.oneof_effects:
        for one in oneof_effect:
            # add_lists.update(set(one.add_effects))
            add_lists.update(set(one.add_effects)-set(initial_state.predicates))
            ## conditional when effect
            for effect in one.when_effects:
                (pos_cnd_lst, neg_cnd_lst, pos_eff_lst, neg_eff_lst) = effect
                if state.is_true(pos_cnd_lst, neg_cnd_lst):
                    # add_lists.update(set(pos_eff_lst))
                    add_lists.update(set(pos_eff_lst)-set(initial_state.predicates))

    return add_lists

#################################################################
class ConcurrentAction(object):

    def __init__(self, action, level, add_list={}, next_levels=[]):
        '''
        @action - an action of the plan
        @level - a tuple of position of @action - its level in the plan and its position in a step
        @add_list - @action's add_effects
        @next_levels - a list of levels that will come after @action (step outcomes)
        '''
        self.level = level
        self.action = action
        self.add_list = add_list
        self.next_levels = next_levels

    def __str__(self):
        string = str(self.level)
        string += ' {}'.format(str(self.action))
        # string += ' [add_list: {}]'.format(self.add_list)
        string += ' {}'.format(str(self.next_levels))
        return string

class ConcurrentExecution(object):

    def __init__(self, actions, state, add_list):
        '''
        @execution - a list of ConcurrentAction belonging to a sequence of execution
        @state - the output state of actions in the execution list
        @add_list - accumulated add_effects 
        '''
        self.actions = actions
        self.state = state
        self.add_list = add_list


#################################################################
def get_concurrent_executions(policy, plan):
    '''
    return a list of sub-plans that can be run in parallel and 
    intersections between sub-plans
    '''
    # a list of ConcurrentExecution of ConcurrentAction
    concurrent_executions =list()

    initial_state = policy.problem.initial_state

    queue = [(next(iter(plan)), initial_state)] # [root]
    visited = [] # [root]

    while len(queue) > 0:

        (root, state) = queue.pop(0) # FIFO
        visited.append(root)

        if root == 'GOAL': continue
        if root in plan and (plan[root] == 'GOAL' or plan[root] == None): continue
        if root not in plan: continue

        ## unfold plan step at current root position
        (step, outcomes) = plan[root]

        if root == next(iter(plan)): ## happens only in the first iteration to initialize
            for i, action in enumerate(step):

                # make ConcurrentAction objects for each action
                # all possible add_list of action
                add_list = add_effects(action, state, initial_state)

                # next levels of the action
                next_levels = set([level for ((add_eff, del_eff), level) in outcomes])
                
                con_act = ConcurrentAction(action=action, level=root, \
                        add_list=add_list, next_levels=next_levels)

                # make ConcurrentExecution objects for each action
                concurrent_executions.append(ConcurrentExecution( \
                    actions=[con_act], state=state, add_list=add_list))

        else:
            # create new ConcurrentAction objects for actions in the current step
            for i, action in enumerate(step):
                for con_execution in concurrent_executions:
                    if len(con_execution.add_list.intersection(set(action.preconditions.pos_preconditions))) > 0:
                        # make ConcurrentAction objects for each action
                        # all possible add_list of action
                        add_list = add_effects(action, state, initial_state)

                        # next levels of the action
                        next_levels = set([level for ((add_eff, del_eff), level) in outcomes])
                        
                        con_act = ConcurrentAction(action=action, level=root, \
                                add_list=add_list, next_levels=next_levels)

                        # append action to con_execution
                        con_execution.actions.append(con_act)
                        con_execution.state = state
                        con_execution.add_list.update(add_list)

            # add actions in the current step that did not have any precedence in concurrent_executions
            for i, action in enumerate(step):
                if not action in [con_act.action \
                    for con_exe in concurrent_executions \
                        for con_act in con_exe.actions]:
                    # make ConcurrentAction objects for each action
                    # all possible add_list of action
                    add_list = add_effects(action, state, initial_state)

                    # next levels of the action
                    next_levels = set([level for ((add_eff, del_eff), level) in outcomes])
                    
                    con_act = ConcurrentAction(action=action, level=root, \
                            add_list=add_list, next_levels=next_levels)

                    ## make ConcurrentExecution objects for each action
                    concurrent_executions.append(ConcurrentExecution( \
                        actions=[con_act], state=state, add_list=add_list))


        ## apply 'step' in the current state and get possible states 
        states = policy.apply_step(state, [action.sig for action in step])

        ## extend for the outcomes of 'step'
        for outcome in outcomes:
            if outcome[1] == 'GOAL': continue
            if outcome[1] in visited: continue
            if outcome[1] in queue: continue

            for state in states.keys():
                if set(outcome[0][0]).issubset(state.predicates):
                    queue.append((outcome[1], state))
                    break

    return concurrent_executions


#################################################################
if __name__ == '__main__':

    args = parse()

    ## make a policy given domain and problem
    policy = Planner(args.domain, args.problem, args.planner)

    ## transform the produced policy into a contingency plan and print it
    plan = policy.plan()
    policy.print_plan(plan=plan)

    ## generate a graph of the policy as a dot file in graphviz
    if args.dot:
        dot_file = gen_dot_plan(plan=plan, dot_file=args.problem)
        print(fg_yellow('-- dot file: ') + dot_file + '\n')
        os.system('xdot %s &' % dot_file)


    concurrent_executions = get_concurrent_executions(policy, plan)

    for con_exe in concurrent_executions:
        print('==================')
        for con_act in con_exe.actions:
            print(con_act)
    exit()

    #############################
    ## create a graphviz object
    dot_filename = '{}.gv'.format(os.path.splitext(args.problem)[0])
    prob_name = os.path.splitext(os.path.basename(args.problem))[0]

    g = Digraph(name=prob_name, filename=dot_filename, strict=1,
        node_attr={'fontname':'helvetica','shape':'ellipse'},
        edge_attr={'fontname':'helvetica'})

    for con_action in concurrent_executions:
        if con_action.next_actions == 'GOAL': continue
        if con_action.next_actions:
            for (root, pos) in con_action.next_actions:
                (step, outcomes) = plan[root]
                label = '+ {}'.format(str(' '.join(map(str,[str('('+' '.join(eff)+')') for eff in \
                    con_action.add_list]))))
                    # con_action.add_list.intersection(step[pos].preconditions.pos_preconditions)]))))
                # g.edge(str(con_action.action), str(step[pos]))
                g.edge(str(con_action.action), str(step[pos]), label=label)

    g.view()

    # for con_action in concurrent_executions:
    #     print(con_action.action, con_action.next_actions)

    # # print(fg_yellow('-- plan_dot_file:'), dot_filename)

    ## print out sub-paths in the plan
    paths = policy.get_paths(plan)
    policy.print_paths(paths=paths, del_effects_included=True, verbose=args.verbose)

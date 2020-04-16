# [THIS IS AN EXPERIMENTAL VERSION AND ONLY WORKS FOR DETERMINISTIC PLANS!]
# transforms a plan into a multi-agent plan and generates two json files 
# for plan and actions descriptions

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
def add_list(action, state, initial_state):
    '''returns all positive effects of @action applicable in @state'''

    # add_lists = set(action.effects.add_effects)
    add_lists = set(action.effects.add_effects)-set(initial_state.predicates)

    # conditional when effect
    for effect in action.effects.when_effects:
        (pos_cnd_lst, neg_cnd_lst, pos_eff_lst, neg_eff_lst) = effect
        if state.is_true(pos_cnd_lst, neg_cnd_lst):
            # add_lists.update(set(pos_eff_lst))
            add_lists.update(set(pos_eff_lst)-set(initial_state.predicates))

    # probabilistic effects
    for prob_effect in action.prob_effects:
        for prob in prob_effect:
            # add_lists.update(set(prob[1].add_effects))
            add_lists.update(set(prob[1].add_effects)-set(initial_state.predicates))
            # conditional when effect
            for effect in prob[1].when_effects:
                (pos_cnd_lst, neg_cnd_lst, pos_eff_lst, neg_eff_lst) = effect
                if state.is_true(pos_cnd_lst, neg_cnd_lst):
                    # add_lists.update(set(pos_eff_lst))
                    add_lists.update(set(pos_eff_lst)-set(initial_state.predicates))

    # non-deterministic effects
    for oneof_effect in action.oneof_effects:
        for one in oneof_effect:
            # add_lists.update(set(one.add_effects))
            add_lists.update(set(one.add_effects)-set(initial_state.predicates))
            # conditional when effect
            for effect in one.when_effects:
                (pos_cnd_lst, neg_cnd_lst, pos_eff_lst, neg_eff_lst) = effect
                if state.is_true(pos_cnd_lst, neg_cnd_lst):
                    # add_lists.update(set(pos_eff_lst))
                    add_lists.update(set(pos_eff_lst)-set(initial_state.predicates))

    return add_lists

#################################################################
def concurrent_executions(policy, plan):
    '''
    return a list of sub-plans that can be run in parallel as well as 
    joint_executions between sub-plans
    '''
    single_executions =list()
    joint_executions = OrderedDict()

    initial_state = policy.problem.initial_state

    queue = [(0, initial_state, [])] # [(root, state, add_lists)]
    visited = []

    while len(queue) > 0:

        (root, state, add_lists) = queue.pop(0) # FIFO
        visited.append(root)

        if root in plan and (plan[root] == 'GOAL' or plan[root] == None): continue
        if root == 'GOAL': continue

        # unfold plan step at current root position
        (step, outcomes) = plan[root]

        new_add_lists = [add_list for add_list in add_lists]

        if root == 0: # happens only in the first iteration to initialize
            for i, action in enumerate(step):
                # create a ConcurrentAction object for each action
                single_executions.append({ root : (set([action]), set([level for ((add_eff, del_eff), level) in outcomes])) })
                new_add_lists.append(add_list(action, state, initial_state))
        else:
            for action in step:
                # create a ConcurrentAction object for each action
                # test all possible intersections
                results = [i for i, add_list in enumerate(add_lists) if len(add_list.intersection(set(action.preconditions.pos_preconditions))) > 0]
                if len(results) == 1: # only one is True (append action to a single_execution)
                    single_executions[results[0]].setdefault(root, (set(),set()))[0].add(action)
                    single_executions[results[0]].setdefault(root, (set(),set()))[1].update(set([out[1] for out in outcomes]))
                    new_add_lists[results[0]].update(add_list(action, state, initial_state))
                elif len(results) == 0: # all are False (no intersection; add a new single_execution)
                    single_executions.append({root:(set([action]), set([out[1] for out in outcomes]))})
                    new_add_lists.append(add_list(action, state, initial_state))
                else: # some joint_executions (add action to joint_executions)
                    joint_executions.setdefault(root, (set(), set()))[0].add(action)
                    joint_executions.setdefault(root, (set(), set()))[1].update(set([out[1] for out in outcomes]))
                    for i in results: new_add_lists[i].update(add_list(action, state, initial_state))

        # apply 'step' in the current state and get possible states 
        states = policy.apply_step(state, [action.sig for action in step])

        # extend for the outcomes of 'step'
        for outcome in outcomes:
            if outcome == 'GOAL': continue
            if outcome[1] in visited: continue

            for state in states.keys():
                if set(outcome[0][0]).issubset(state.predicates):
                    queue.append((outcome[1], state, new_add_lists))
                    break

    return single_executions, joint_executions

#################################################################
def concurrent_subplans(policy, plan):
    '''returns a fully multi-agent partial-order plan'''
    # get possible concurrent and joint executions
    single_executions, joint_executions = concurrent_executions(policy, plan)

    # find the final plan's main list boundaries/clusters 
    main_list_borders = set(joint_executions.keys()) | {max(plan.keys())+1}
    for single_execution in single_executions:
        root = 0
        for i in sorted(single_execution.keys()):
            if abs(root-i) > 1: main_list_borders.add(i)
            root = i

    # build the main list of the final partial plan ordered by keys as in main_list_borders.
    # main_list is executed in total-ordering and each block/cluster in the main_list 
    # is a list of dictionaries as partial-order sub_plans.
    main_list = OrderedDict()

    root = 0
    for main_list_border in sorted(main_list_borders):
        # make an empty list of sub_plans at every block (i.e. every main_list_border)
        main_list[root] = []

        # extract a sub_plan in every single_execution by keys in range(root, main_list_border)
        # and append it to main_list[root]
        for single_execution in single_executions:
            sub_plan = OrderedDict([(key,single_execution[key]) \
                for key in range(root, main_list_border) if key in single_execution])
            if sub_plan: main_list[root].append(sub_plan)

        # add also partial_plans in joint_executions into main_list
        if root in joint_executions.keys():
            main_list[root].append(OrderedDict({root:list(joint_executions[root])}))

        root = main_list_border

    return main_list

#################################################################
def action_json(action):
    '''convert a grounded action into a json dictionary and return it'''
    action_json = OrderedDict()
    action_json['name'] = action.sig[0]
    action_json['args'] = action.sig[1:]
    action_json['pre'] = action.preconditions.pos_preconditions
    if action.effects.add_effects and not action.oneof_effects and not action.prob_effects:
        action_json.setdefault('post', []).append(action.effects.add_effects)
    for oneof_effect in action.oneof_effects:
        for one in oneof_effect:
            if one.add_effects:
                action_json.setdefault('post', []).append(action.effects.add_effects+one.add_effects)
    for prob_effect in action.prob_effects:
        for prob in prob_effect:
            if prob[1].add_effects:
                action_json.setdefault('post', []).append(action.effects.add_effects+prob[1].add_effects)

    return action_json

#################################################################
def json_ma_plan(policy, verbose=False):
    '''
    Convert given plan into a concurrent plan for execution by multi-robot.
    The output is partial parallel plan iff the given plan is partial-order.
    '''
    # get the first pre-order path
    path = policy.get_paths(policy.plan())[0]
    if verbose: policy.print_plan(path)

    # get concurrent executions in concurrent clusters
    concurrent_subplans_lists = concurrent_subplans(policy, path)

    main_list = OrderedDict()

    # temporary: ignore outcomes of every step in subplans
    for key, subplans in concurrent_subplans_lists.items():
        new_subplans = []
        for subplan in subplans:
            new_subplan = OrderedDict()
            for k, (actions, outcomes) in subplan.items():
                new_subplan[k] = list(actions)
            new_subplans.append(new_subplan)
        main_list[key] = new_subplans

    plan_json = OrderedDict()
    action_descriptions_json = OrderedDict()
    plan_json['main'] = OrderedDict({'list':[],'ordering':'total'})

    for n, (key, subplans) in enumerate(main_list.items()):
        # -------------------------------------------------------------------------------
        if len(subplans) == 1: # there is only one parallel subplan
            # ----------------------------------------------------
            if len(subplans[0]) == 1: # there is only one step in this subplan
                # ----------------------------------------------------
                if len(subplans[0][key]) == 1: # there is only one action in this step
                    # make a reference to action (key+i)
                    action_ref = 'action_{}'.format(n)
                    # add ref to main list of the plan
                    plan_json['main']['list'].append(action_ref)
                    # add ref and its description into the action_descriptions_json
                    action_descriptions_json[action_ref] = action_json(subplans[0][key][0])
                # ----------------------------------------------------
                else: # there are more actions in this step
                    # make a reference to subplan (n)
                    subplan_ref = 'subplan_{}'.format(n)
                    plan_json['main']['list'].append(subplan_ref)
                    plan_json[subplan_ref] = OrderedDict({'list':[],'ordering':'partial'})
                    for i, action in enumerate(subplans[0][key]):
                        # make a reference to action (n+i+j)
                        action_ref = 'action_{}_{}'.format(n,i)
                        # add ref to main list of the plan
                        plan_json[subplan_ref]['list'].append(action_ref)
                        # add ref and its description into the action_descriptions_json
                        action_descriptions_json[action_ref] = action_json(action)
            # ----------------------------------------------------
            else: # there are more steps in this subplan
                # make a reference to subplan (n)
                subplan_ref = 'subplan_{}'.format(n)
                plan_json['main']['list'].append(subplan_ref)
                plan_json[subplan_ref] = OrderedDict({'list':[],'ordering':'total'})
                for i, (k, step) in enumerate(subplans[0].items()):
                    # ----------------------------------------------------
                    if len(step) == 1: # there is only one action in this step
                        # make a reference to action (key+i)
                        action_ref = 'action_{}_{}'.format(n,i)
                        # add ref to main list of the plan
                        plan_json[subplan_ref]['list'].append(action_ref)
                        # add ref and its description into the action_descriptions_json
                        action_descriptions_json[action_ref] = action_json(subplans[0][key][0])
                    # ----------------------------------------------------
                    else: # there are more actions in this step
                        # make a reference to subplan (n)
                        subsubplan_ref = 'subplan_{}_{}'.format(n,i)
                        plan_json[subplan_ref]['list'].append(subsubplan_ref)
                        plan_json[subsubplan_ref] = OrderedDict({'list':[],'ordering':'partial'})
                        for j, action in enumerate(step):
                            # make a reference to action (n+i+j)
                            action_ref = 'action_{}_{}_{}'.format(n,i,j)
                            # add ref to main list of the plan
                            plan_json[subsubplan_ref]['list'].append(action_ref)
                            # add ref and its description into the action_descriptions_json
                            action_descriptions_json[action_ref] = action_json(action)
        # -------------------------------------------------------------------------------
        else: # there are more parallel subplans
            # make a reference to subplan (n)
            subplan_ref = 'subplan_{}'.format(n)
            plan_json['main']['list'].append(subplan_ref)
            plan_json[subplan_ref] = OrderedDict({'list':[],'ordering':'partial'})
            for i, subplan in enumerate(subplans):
                # ----------------------------------------------------
                if len(subplan) == 1: # there is one step in this subplan
                    # ----------------------------------------------------
                    if len(list(subplan.values())[0]) == 1: # there is only one action in this step
                        # make a reference to action (key+i)
                        action_ref = 'action_{}_{}'.format(n,i)
                        # add ref to main list of the plan
                        plan_json[subplan_ref]['list'].append(action_ref)
                        # add ref and its description into the action_descriptions_json
                        action_descriptions_json[action_ref] = action_json(list(subplan.values())[0][0])
                    # ----------------------------------------------------
                    else: # there are more actions in this step
                        # make a reference to subplan (n)
                        subsubplan_ref = 'subplan_{}_{}'.format(n,i)
                        plan_json[subplan_ref]['list'].append(subsubplan_ref)
                        plan_json[subsubplan_ref] = OrderedDict({'list':[],'ordering':'partial'})
                        for j, action in enumerate(list(subplan.values())[0]):
                            # make a reference to action (n+i+j)
                            action_ref = 'action_{}_{}_{}'.format(n,i,j)
                            # add ref to main list of the plan
                            plan_json[subsubplan_ref]['list'].append(action_ref)
                            # add ref and its description into the action_descriptions_json
                            action_descriptions_json[action_ref] = action_json(action)
                # ----------------------------------------------------
                else: # there are more steps in this subplan
                    # make a reference to subplan (n+i)
                    subsubplan_ref = 'subplan_{}_{}'.format(n,i)
                    plan_json[subplan_ref]['list'].append(subsubplan_ref)
                    plan_json[subsubplan_ref] = OrderedDict({'list':[],'ordering':'total'})
                    for j, (k, step) in enumerate(subplan.items()):
                        # ----------------------------------------------------
                        if len(step) == 1: # there is only one action in this step
                            # make a reference to action (key+i)
                            action_ref = 'action_{}_{}_{}'.format(n,i,j)
                            # add ref to main list of the plan
                            plan_json[subsubplan_ref]['list'].append(action_ref)
                            # add ref and its description into the action_descriptions_json
                            action_descriptions_json[action_ref] = action_json(step[0])
                        # ----------------------------------------------------
                        else: # there are more actions in this step
                            # make a reference to subplan (n)
                            subsubsubplan_ref = 'subplan_{}_{}_{}'.format(n,i,j)
                            plan_json[subsubplan_ref]['list'].append(subsubsubplan_ref)
                            plan_json[subsubsubplan_ref] = OrderedDict({'list':[],'ordering':'partial'})
                            for l, action in enumerate(step):
                                # make a reference to action (n+i+j)
                                action_ref = 'action_{}_{}_{}_{}'.format(n,i,j,l)
                                # add ref to main list of the plan
                                plan_json[subsubsubplan_ref]['list'].append(action_ref)
                                # add ref and its description into the action_descriptions_json
                                action_descriptions_json[action_ref] = action_json(action)

    plan_json['actions'] = list(action_descriptions_json.keys())

    # make json files for plan and actions descriptions
    plan_json_str = json.dumps(plan_json, indent=4)
    action_json_str = json.dumps(action_descriptions_json, indent=4)

    plan_json_file = '{}.plan.json'.format(os.path.splitext(policy.problem_file)[0])
    actions_json_file = '{}.actions.json'.format(os.path.splitext(policy.problem_file)[0])

    with open(plan_json_file, 'w') as outfile:
        json.dump(json.loads(plan_json_str, object_pairs_hook=OrderedDict), outfile, sort_keys=False, indent=4)

    with open(actions_json_file, 'w') as outfile:
        json.dump(json.loads(action_json_str, object_pairs_hook=OrderedDict), outfile, sort_keys=False, indent=4)

    return plan_json_file, actions_json_file


def merge_dict(d1, d2):
    merged_dict = OrderedDict()
    keys = set(d1.keys()) | set(d2.keys())
    for key in keys:
        if key in d1 and key in d2:
            merged_dict[key] = (set(d1[key])[0] | set(d2[key][0]), set(d1[key])[1] | set(d2[key][1]))
        elif key in d1:
            merged_dict[key] = d1[key]
        else:
            merged_dict[key] = d2[key]
    return merged_dict

#################################################################
if __name__ == '__main__':

    args = parse()

    # make a policy given domain and problem
    policy = Planner(args.domain, args.problem, args.planner)

    # transform the produced policy into a contingency plan and print it
    plan = policy.plan()
    policy.print_plan(plan=plan)

    # generate a graph of the policy as a dot file in graphviz
    if args.dot:
        dot_file = gen_dot_plan(plan=plan, dot_file=args.problem)
        print(fg_yellow('-- dot file: ') + dot_file + '\n')
        os.system('xdot %s &' % dot_file)

    paths = policy.get_paths(plan, verbose=args.verbose)
    policy.print_paths(paths=paths, del_effects_included=True, verbose=args.verbose)

    plan = paths[0]

    #############################
    # get possible concurrent and joint executions
    single_executions, joint_executions = concurrent_executions(policy, plan)

    if args.verbose:
        print(fg_yellow('----------------------------------'))
        print(fg_yellow('-- possible concurrent executions'))
        print(fg_yellow('----------------------------------'))
        for i, single_execution in enumerate(single_executions):
            print(fg_yellow('-- execution_{}'.format(str(i))))
            for level, (actions, outcomes) in sorted(single_execution.items()):
            # for level, (actions, outcomes) in sorted(merge_dict(single_execution,joint_executions).items()):
                print('{} : {} {}'.format(str(level), ' '.join(map(str, actions)), outcomes))

        print(fg_yellow('-- joint executions'))
        for level, (actions, outcomes) in joint_executions.items():
            print('{} : {} {}'.format(str(level), ' '.join(map(str, actions)), outcomes))

    #############################
    # refine and separate the concurrent executions into concurrent clusters
    main_list = concurrent_subplans(policy, plan)

    if args.verbose:
        print(fg_yellow('\n----------------------------------'))
        print(fg_yellow('-- actual multi-agent plan'))
        print(fg_yellow('----------------------------------'))

        for i, (key, subplans) in enumerate(main_list.items()):
            print(fg_yellow('---------------------------------- block_{}'.format(str(i))))
            for j, subplan in enumerate(subplans):
                if(len(subplans)) > 1: print(fg_beige('-- subplan_{}'.format(str(j))))
                for k, (actions, outcomes) in subplan.items():
                    print('{} -- {} {}'.format(k, ' '.join(map(str, actions)), outcomes))

    # #############################
    # # create a graphviz object
    # dot_filename = '{}.gv'.format(os.path.splitext(args.problem)[0])
    # prob_name = os.path.splitext(os.path.basename(args.problem))[0]

    # g = Digraph(name=prob_name, filename=dot_filename, strict=False,
    #     node_attr={'fontname':'helvetica','shape':'ellipse'},
    #     edge_attr={'fontname':'helvetica'})

    # for i, single_execution in enumerate(single_executions):
    #     for level, (actions, outcomes) in single_execution.items():
    #         g.node('n{}{}'.format(str(i), str(level)), label=' '.join(map(str, actions)))
    #         for outcome in outcomes:
    #             if not outcome == 'GOAL':
    #                 if outcome in single_execution.keys():
    #                     g.edge('n{}{}'.format(str(i), str(level)), 'n{}{}'.format(str(i), str(outcome)), label=str(outcome))
    #                 else:
    #                     for j, single_exe in enumerate(single_executions):
    #                         if outcome in single_exe.keys():
    #                             g.edge('n{}{}'.format(str(i), str(level)), 'n{}{}'.format(str(j), str(outcome)), label=str(outcome))
    #                     if outcome in joint_executions.keys():
    #                         g.edge('n{}{}'.format(str(i), str(level)), 'n{}{}'.format(str(len(single_executions)),str(outcome)), label=str(outcome))
    #                 for j, single_exe in enumerate(single_executions):
    #                     if not level in single_exe.keys() and outcome in single_exe.keys():
    #                         g.edge('n{}{}'.format(str(i), str(level)), 'n{}{}'.format(str(j), str(outcome)), label=str(outcome))

    # for level, (actions, outcomes) in joint_executions.items():
    #     g.node('n{}{}'.format(str(len(single_executions)),str(level)), label=' '.join(map(str, actions)))
    #     for outcome in outcomes:
    #         if not outcome == 'GOAL':
    #             for j, single_exe in enumerate(single_executions):
    #                 if outcome in single_exe.keys():
    #                     g.edge('n{}{}'.format(str(len(single_executions)),str(level)), 'n{}{}'.format(str(j), str(outcome)), label=str(outcome))
    #             if outcome in joint_executions.keys():
    #                 g.edge('n{}{}'.format(str(level)), 'n{}{}'.format(str(len(single_executions)),str(outcome)), label=str(outcome))

    # g.view()


    #############################
    # convert the plan inti a concurrent plan in json files
    plan_json_file, actions_json_file = json_ma_plan(policy)

    print(fg_yellow('-- plan_json_file:'), plan_json_file)
    print(fg_yellow('-- actions_json_file:'), actions_json_file)
    os.system('cd lua && lua json_multiagent_plan.lua ../%s &' % plan_json_file)
    os.system('xdot %s.dot &' % plan_json_file)
    print()

    print('Planning time: %.3f s' % policy.planning_time)
    print('Total number of replannings: %i' % policy.planning_call)
    print('Total number of calls to unsolvable states: %i' % policy.unsolvable_call)

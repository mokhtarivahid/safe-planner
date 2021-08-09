# [THIS IS AN EXPERIMENTAL VERSION AND ONLY WORKS FOR DETERMINISTIC PLANS!]
# transforms a plan into a multi-agent plan and generates two json files 
# for plan and actions descriptions

#!/usr/bin/env python

import argparse
import os, time, sys
import json
from collections import OrderedDict, defaultdict
from graphviz import Digraph

import color

def parse_args(dir_path=''):
    usage = 'python3 main.py <DOMAIN> <PROBLEM> [<PLANNER>] [-d] [-v] [-h]'
    description = "Safe-Planner is a non-deterministic planner for PPDDL."
    parser = argparse.ArgumentParser(usage=usage, description=description)

    parser.add_argument('domain',  nargs='?', type=str, help='path to a PDDL domain file')
    parser.add_argument('problem', nargs='?', type=str, help='path to a PDDL problem file')
    parser.add_argument("-a", "--agents", nargs='+', type=str, default=[], 
        help="a list of agents: e.g., -a left_arm right_arm")
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


#################################################################
def add_effects(action, state, initial_state):
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
def concurrent_executions(policy, plan, agents=[]):
    '''
    return a list of sub-plans that can be run in parallel as well as 
    joint_executions between sub-plans
    '''
    single_executions = [ dict() for _ in range(len(agents)) ]
    joint_executions = OrderedDict()

    for level, step in plan.items():

        if step == 'GOAL' or step == None: continue

        # unfold step into a tuple of actions and outcomes
        (actions, outcomes) = step

        for action in actions:
            # if all agents participate in the action
            if len(set(action.sig[1:]).intersection(set(agents))) > 1:
                joint_executions.setdefault(level, (set(), set()))[0].add(action)
                joint_executions.setdefault(level, (set(), set()))[1].update(set([out[1] for out in outcomes]))

            # if no agents participate in the action
            elif len(set(action.sig[1:]).intersection(set(agents))) == 0:
                single_executions.append({ level : ({action}, set([l for ((_, _), l) in outcomes])) })

            # if one agent participates in the action
            else:
                for i, agent in enumerate(agents):
                    if agent in action.sig[1:]:
                        # create a ConcurrentAction object for each action
                        single_executions[i].setdefault(level, (set(),set()))[0].add(action)
                        single_executions[i].setdefault(level, (set(),set()))[1].update(set([out[1] for out in outcomes]))

    return single_executions, joint_executions

#################################################################
def _concurrent_executions(policy, plan, agents=[]):
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

        if root not in plan: continue
        if root == 'GOAL' or plan[root] == 'GOAL' or plan[root] == None: continue

        # unfold plan step at current root position
        (step, outcomes) = plan[root]

        new_add_lists = [add_list for add_list in add_lists]

        if root == 0: # happens only in the first iteration to initialize
            if len(agents) == 0:
                for action in step:
                    # create a ConcurrentAction object for each action
                    if len(single_executions) > 0:
                        single_executions[0].setdefault(root, (set(),set()))[0].add(action)
                        single_executions[0].setdefault(root, (set(),set()))[1].update(set([out[1] for out in outcomes]))
                        new_add_lists[0].update(add_effects(action, state, initial_state))
                    else:
                        single_executions.append({ root : (set([action]), set([level for ((add_eff, del_eff), level) in outcomes])) })
                        new_add_lists.append(add_effects(action, state, initial_state))
            for i, agent in enumerate(agents):
                for action in step:
                    if agent in action.sig[1:]:
                        # create a ConcurrentAction object for each action
                        if i < len(single_executions):
                            single_executions[i].setdefault(root, (set(),set()))[0].add(action)
                            single_executions[i].setdefault(root, (set(),set()))[1].update(set([out[1] for out in outcomes]))
                            new_add_lists[i].update(add_effects(action, state, initial_state))
                        else:
                            single_executions.append({ root : (set([action]), set([level for ((add_eff, del_eff), level) in outcomes])) })
                            new_add_lists.append(add_effects(action, state, initial_state))
        else:
            for action in step:
                # create a ConcurrentAction object for each action
                # test all possible intersections
                results = [i for i, add_list in enumerate(add_lists) if len(add_list.intersection(set(action.preconditions.pos_preconditions))) > 0]
                if len(results) == 1: # only one is True (append action to a single_execution)
                    single_executions[results[0]].setdefault(root, (set(),set()))[0].add(action)
                    single_executions[results[0]].setdefault(root, (set(),set()))[1].update(set([out[1] for out in outcomes]))
                    new_add_lists[results[0]].update(add_effects(action, state, initial_state))
                elif len(results) == 0: # all are False (no intersection; add a new single_execution)
                    single_executions.append({root:(set([action]), set([out[1] for out in outcomes]))})
                    new_add_lists.append(add_effects(action, state, initial_state))
                else: # some joint_executions (add action to joint_executions)
                    joint_executions.setdefault(root, (set(), set()))[0].add(action)
                    joint_executions.setdefault(root, (set(), set()))[1].update(set([out[1] for out in outcomes]))
                    for i in results: new_add_lists[i].update(add_effects(action, state, initial_state))

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
def concurrent_subplans(policy, plan, agents=[]):
    '''returns a fully multi-agent partial-order plan'''
    # get possible concurrent and joint executions
    single_executions, joint_executions = concurrent_executions(policy, plan, agents)

    # find the final plan's main list boundaries/clusters 
    main_list_borders = set(joint_executions.keys()) | {max([k for k in plan.keys() if isinstance(k,int)])+1}
    for single_execution in single_executions:
        # always add the first key in the current single_execution
        if len(single_execution.keys()) > 0:
            main_list_borders.add(min(single_execution.keys()))

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

    # divide action's preconditions into two disjoint sets of pre- and per-conditions 
    per_conditions = set(action.preconditions.pos_preconditions)-set(action.effects.del_effects)
    pre_conditions = set(action.preconditions.pos_preconditions)-per_conditions

    action_json = OrderedDict()
    action_json['name'] = action.sig[0]
    action_json['args'] = action.sig[1:]
    action_json['pre'] = OrderedDict([(prec[0], prec[1:]) for prec in pre_conditions])
    action_json['per'] = OrderedDict([(prec[0], prec[1:]) for prec in per_conditions])
    action_json['add'] = OrderedDict([(eff[0], eff[1:]) for eff in action.effects.add_effects])
    action_json['del'] = OrderedDict([(eff[0], eff[1:]) for eff in action.effects.del_effects])

    # action_json['pre'] = action.preconditions.pos_preconditions
    # if action.effects.add_effects and not action.oneof_effects and not action.prob_effects:
    #     action_json.setdefault('post', []).append(action.effects.add_effects)
    # for oneof_effect in action.oneof_effects:
    #     for one in oneof_effect:
    #         if one.add_effects:
    #             action_json.setdefault('post', []).append(action.effects.add_effects+one.add_effects)
    # for prob_effect in action.prob_effects:
    #     for prob in prob_effect:
    #         if prob[1].add_effects:
    #             action_json.setdefault('post', []).append(action.effects.add_effects+prob[1].add_effects)

    return action_json

#################################################################
def json_ma_plan(policy, agents=[], full=False, verbose=False):
    '''
    Convert given plan into a concurrent plan for execution by multi-robot.
    The output is partial parallel plan iff the given plan is partial-order.
    '''
    # get the first pre-order path
    try:
        if full:
            path = policy.plan()
        else:
            path = policy.get_paths(policy.plan())[0]
    except:
        return None

    if verbose: 
        print(color.fg_red('[EXPERIMENTAL JSON PLAN!]'))
        print(color.fg_red('[APPLIED ONLY TO THE FIRST PRE-ORDER PATH OF THE PLAN]'))
        policy.print_plan(path)

    # get concurrent executions in concurrent clusters
    concurrent_subplans_lists = concurrent_subplans(policy, path, agents)

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
                    action_ref = '_'.join(subplans[0][key][0].sig)
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
                        action_ref = '_'.join(action.sig)
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
                        action_ref = '_'.join(step[0].sig)
                        # add ref to main list of the plan
                        plan_json[subplan_ref]['list'].append(action_ref)
                        # add ref and its description into the action_descriptions_json
                        action_descriptions_json[action_ref] = action_json(step[0])
                    # ----------------------------------------------------
                    else: # there are more actions in this step
                        # make a reference to subplan (n)
                        subsubplan_ref = 'subplan_{}_{}'.format(n,i)
                        plan_json[subplan_ref]['list'].append(subsubplan_ref)
                        plan_json[subsubplan_ref] = OrderedDict({'list':[],'ordering':'partial'})
                        for j, action in enumerate(step):
                            # make a reference to action (n+i+j)
                            action_ref = 'action_{}_{}_{}'.format(n,i,j)
                            action_ref = '_'.join(action.sig)
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
                        action_ref = '_'.join(list(subplan.values())[0][0].sig)
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
                            action_ref = '_'.join(action.sig)
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
                            action_ref = '_'.join(step[0].sig)
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
                                action_ref = '_'.join(action.sig)
                                # add ref to main list of the plan
                                plan_json[subsubsubplan_ref]['list'].append(action_ref)
                                # add ref and its description into the action_descriptions_json
                                action_descriptions_json[action_ref] = action_json(action)

    plan_json['actions'] = list(action_descriptions_json.keys())

    # make json files for plan and actions descriptions
    plan_json_str = json.dumps(plan_json, indent=4)
    action_json_str = json.dumps(action_descriptions_json, indent=4)

    if policy.problem_file is not None:
        problem_file = policy.problem_file
    else:
        problem_file = policy.domain_file

    plan_json_file = '{}.plan.json'.format(os.path.splitext(problem_file)[0])
    actions_json_file = '{}.actions.json'.format(os.path.splitext(problem_file)[0])

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

    import planner
    import dot_plan

    # parse and refine relative input paths as well as arguments
    args = parse_relative_path()

    # make a policy given domain and problem
    policy = planner.Planner(args.domain, args.problem, args.planners, args.rank, args.verbose)

    # transform the produced policy into a contingency plan and print it
    plan = policy.plan()
    path = policy.get_paths(policy.plan())[0]
    policy.print_plan(plan=path)

    #############################
    # get possible concurrent and joint executions
    single_executions, joint_executions = concurrent_executions(policy, path, args.agents)

    if args.verbose:
        print(color.fg_yellow('----------------------------------'))
        print(color.fg_yellow('-- possible concurrent executions'))
        print(color.fg_yellow('----------------------------------'))
        for i, single_execution in enumerate(single_executions):
            print(color.fg_yellow('-- execution_{}'.format(str(i))))
            for level, (actions, outcomes) in sorted(single_execution.items()):
            # for level, (actions, outcomes) in sorted(merge_dict(single_execution,joint_executions).items()):
                print('{} : {} {}'.format(str(level), ' '.join(map(str, actions)), outcomes))

        print(color.fg_yellow('-- joint executions'))
        for level, (actions, outcomes) in joint_executions.items():
            print('{} : {} {}'.format(str(level), ' '.join(map(str, actions)), outcomes))

    #############################
    # refine and separate the concurrent executions into concurrent clusters
    main_list = concurrent_subplans(policy, path, args.agents)

    if args.verbose:
        print(color.fg_yellow('\n----------------------------------'))
        print(color.fg_yellow('-- actual multi-agent plan'))
        print(color.fg_yellow('----------------------------------'))

        for i, (key, subplans) in enumerate(main_list.items()):
            print(color.fg_yellow('---------------------------------- block_{}'.format(str(i))))
            for j, subplan in enumerate(subplans):
                if(len(subplans)) > 1: print(color.fg_beige('-- subplan_{}'.format(str(j))))
                for k, (actions, outcomes) in subplan.items():
                    print('{} -- {} {}'.format(k, ' '.join(map(str, actions)), outcomes))

    #############################
    # convert the plan inti a concurrent plan in json files
    plan_json_file, actions_json_file = json_ma_plan(policy, args.agents, full=True)

    print(color.fg_yellow('-- plan_json_file:') + plan_json_file)
    print(color.fg_yellow('-- actions_json_file:') + actions_json_file)
    os.system('cd lua && lua json_multiagent_plan.lua ../%s &' % plan_json_file)
    os.system('xdot %s.dot &' % plan_json_file)
    print('')

    # generate a graph of the policy as a dot file in graphviz
    if args.dot:
        dot_file = dot_plan.gen_dot_plan(plan=plan, domain_file=args.domain, problem_file=args.problem)
        print(color.fg_yellow('-- dot file: ') + dot_file + '\n')
        os.system('xdot %s &' % dot_file)

        # transform the plan into a parallel plan
        import dot_ma_plan 
        dot_file, tred_dot_file = dot_ma_plan.parallel_plan(policy, verbose=args.verbose)
        print(color.fg_yellow('-- graphviz file: ') + dot_file)
        print(color.fg_yellow('-- transitive reduction: ') + tred_dot_file)


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

#!/usr/bin/env python3

import os, sys
from collections import OrderedDict, defaultdict, Counter
from time import time
import copy
import itertools

from color import fg_green, fg_red, fg_yellow, fg_blue, fg_voilet, fg_beige, bg_green, bg_red, bg_yellow, bg_blue, bg_voilet
from pddlparser import PDDLParser
from external_planner import call_planner

class Planner(object):

    def __init__(self, domain, problem, planner='ff', verbose=False):
        """
        @arg domain : path to pddl domain (string)
        @arg problem : path to pddl problem (string)
        @arg planner : name of the external planner (string)
        @arg planner : name of the external planner (string)
        @arg verbose : if True, prints out statistics 
        """

        ## the main probabilistic domain object ##
        try:
            self.domain = PDDLParser.parse(domain)
        except:
            print(fg_red("\npddl parser does not support '{0}'!\n".format(domain)))

        ## extract the base name of the given domain: 
        ## the path to the deterministic domains 
        base = os.path.splitext(domain)[0]

        ## a dictionary of deterministic domains: keys as paths to pddl 
        ## domains and values as domain objects -- dict({pddl:object})
        self.domains = OrderedDict()

        ## list of the probabilistic actions names
        self.prob_actions = list()

        ## if the domain is probabilistic
        if ":probabilistic-effects" in self.domain.requirements:
            ## read the probabilistic actions names
            try:
                with open(base+'.prob') as f:
                    self.prob_actions = f.read().splitlines()
            except FileNotFoundError as fnf_error:
                    print(fg_red("\n'"+base+".prob' containing the name of probabilistic actions should exist!\n"))
                    exit()

            ## parse deterministic pddl domains
            for domain in sorted(listdir_fullpath(base)):
                if domain.endswith('.pddl'):
                    self.domains[domain] = PDDLParser.parse(domain)
        else:
            self.domains[domain] = self.domain

        ## parse pddl problem
        self.problem = PDDLParser.parse(problem)

        ## stores the external planner
        self.planner = planner

        self.policy = OrderedDict()

        ## stores states and probabilistic actions which are not yet explored ##
        self.open_stack = OrderedDict({self.problem.initial_state: None})

        ## stores states and actions which lead to dead-ends ##
        self.deadend_list = defaultdict(list)

        self.planning_call = 0

        self.deadends_call = 0

        self.planning_time = time()

        # if new_state is itself a goal state (then the plan is empty)
        if self.problem.initial_state.is_true(*(self.problem.goals, self.problem.num_goals)):
            self.policy[self.problem.initial_state] = None
            if verbose: print(fg_yellow('@@ initial state already contains the goal!'))
            return

        ##
        ## main loop of the planner
        ##
        while self.open_stack:

            # pop items as in LIFO
            (state, action) = self.open_stack.popitem()

            ###################################################################
            if action == None:
                if verbose: print(fg_green('\n>> [make initial plan]'))

                ## create a pddl problem given retrieved 'state' as its initial state ##
                problm_pddl = self.problem.pddl(state)

                policy = OrderedDict()

                for domain, domain_spec in self.domains.items():

                    # ## if state is in deadend_list modify the domain and make inapplicable actions in deadend_list[state]
                    # if state in self.deadend_list:
                    #     domain, domain_spec = self.modify_domain(state, domain, domain_spec)

                    ## print out some info
                    if verbose:
                        print(fg_yellow('@ domain:') + domain)
                        print(fg_yellow('@ problem:') + problm_pddl)

                    plan = call_planner(domain, problm_pddl, self.planner, verbose)

                    self.planning_call += 1

                    ## if no plan exists try the next domain ##
                    if plan == None:
                        if verbose: print(fg_red('@@ no plan exists'))
                        continue

                    policy = self.policy_image(domain_spec, state, plan, verbose)

                    ## check if the policy contains states and actions in the dead-ends list ##
                    if self.has_deadend(policy, verbose):
                        policy = OrderedDict()
                        self.deadends_call += 1
                        continue

                    ## there exists a valid plan: terminate the loop ##
                    break


                ## push the state and probabilistic actions into the self.open_stack 
                ## if {(s, a) exist p | s !exist Sg, s !exist S_\pi, a is probabilistic}
                ## ! currently, we assume only one probabilistic action in each state
                self.push_prob_actions(policy, verbose)

                ## if no such domain nor plan exist ##
                if not policy:
                    if verbose: print(fg_red('@@ no initial plan exists!'))
                    ## put in the dead-ends list all states leading to 'state' and remove their path from policy ##
                    for s, step in [(s, step) for s, step in self.policy.items() \
                                              if state in self.apply_step(s, step, verbose=verbose)]:
                        self.deadend_list[s].append(Counter(step))
                        self.open_stack[s] = None
                        self.remove_path(s, verbose)
                else:
                    ## update global policy ##
                    self.policy.update(policy)

            ###################################################################
            ## if action == None: ##
            else:

                if verbose: print(fg_green("\n>> [expand probabilistic action '{0}']".format(str(action))))

                # valid_plan_for_all = False

                policy = OrderedDict()

                try:
                    new_states = self.apply_step(state, action, verbose=verbose)
                except:
                    print(fg_red("@@ other outcome '{0}' is not applicable!!".format(str(self.policy[state]))))
                    exit()

                ## !!! THIS FOR LOOP HAS TO BE IMPROVED AND UPGRADED TO CHECK 
                ## !!! IF THERE IS A VALID PLAN FOR ALL OUTCOME IN 'NEW_STATES'
                ## !!! CURRENTLTY IT ONLY CHECKS FOR THE FIRST POSSIBLE OUTCOME
                for new_state in new_states:

                    # if new_state is itself a goal state (then the plan is empty)
                    if new_state.is_true(*(self.problem.goals, self.problem.num_goals)): 
                        policy[new_state] = None
                        if verbose: print(fg_yellow('@@ new state already contains the goal!'))
                        continue

                    # in some small problems, the state may become empty by the action application
                    if new_state.is_empty():
                        if verbose: print(fg_red('@@ new state becomes empty!'))
                        break

                    if new_state in self.policy:
                        if verbose: print(fg_red('@@ new state is already visited!'))
                        continue

                    ## a state is dead end if all domains are not applicable in that state
                    ## if a domain is not applicable, i.e., no plan is found, then 'valid_plan_for_some' increases, 
                    ## finally if 'valid_plan_for_some' == len(self.domains) means no valid plan found for all domains
                    valid_plan_for_some = 0

                    ## for every other outcome of 'action' look for if there is a valid plan ##
                    for domain, domain_spec in self.domains.items():

                        # ## if state is in deadend_list modify the domain and make inapplicable actions in deadend_list[state]
                        # if state in self.deadend_list:
                        #     domain, domain_spec = self.modify_domain(state, domain, domain_spec)

                        ## generate a new state and then make plan ##
                        ## update step by replacing 'other_outcome' action with an old outcome
                        ## !! currently we only assume one probabilistic action in a state 


                        # try:
                        #     # new_state = self.apply_step(state, self.policy[state], domain_spec, verbose=verbose)
                        #     new_state = self.apply_step(state, action, domain_spec, verbose=verbose)
                        # except:
                        #     print(fg_red("@@ other outcome '{0}' is not applicable!!".format(str(self.policy[state]))))
                        #     exit()

                        # if new_state in self.policy:
                        #     if verbose: print(fg_red('@@ new state is already visited!'))
                        #     continue

                        # # if new_state is itself a goal state (then the plan is empty)
                        # if new_state.is_true(*(self.problem.goals, self.problem.num_goals)): 
                        #     policy[new_state] = None
                        #     if verbose: print(fg_yellow('@@ new state already contains the goal!'))
                        #     continue

                        # # in some small problems, the state may become empty by the action application
                        # if new_state.is_empty():
                        #     if verbose: print(fg_red('@@ new state becomes empty!'))
                        #     break

                        # ## if state is in deadend_list create a domain with inapplicable actions in deadend_list[state]
                        # if new_state in self.deadend_list:
                        #     ## make a list of excluding action signatures (these actions become inapplicable in the current state)
                        #     ex_actions = [list(act)[0] for act in self.deadend_list[new_state]] ## convert back the Counter to a list
                        #     print(ex_actions)
                        #     domain_spec_cp = copy.deepcopy(domain_spec)
                        #     domain_spec_cp.make_inapplicable(ex_actions, state)
                        #     domain = domain_spec_cp.pddl()
                        #     # del domain_spec_cp
                        #     # domain_spec.make_inapplicable(ex_actions)
                        #     # domain = domain_spec.pddl()

                        ## create a pddl problem of 'new_state' as its initial state ##
                        problm_pddl = self.problem.pddl(new_state)

                        ## print out some info
                        if verbose:
                            print(fg_yellow('@ domain:') + domain)
                            print(fg_yellow('@ problem:') + problm_pddl)

                        plan = call_planner(domain, problm_pddl, self.planner, verbose)

                        self.planning_call += 1

                        ## if no plan exists :- dead ends ##
                        if plan == None:
                            if verbose: print(fg_red('@@ no plan exists'))
                            valid_plan_for_some += 1
                            continue
                            # break

                        policy.update(self.policy_image(domain_spec, new_state, plan, verbose))

                        ## check if the plan contains states and actions in the dead-ends list ##
                        if self.has_deadend(policy, verbose):
                            policy = OrderedDict()
                            self.deadends_call += 1
                            break

                    else:
                        ## continue if the loop works for all (the inner for-loop wasn't broken)
                        if valid_plan_for_some == len(self.domains):
                            if verbose: print(fg_red('@@ no valid plan for all domains'))
                            break
                        if verbose: print(fg_red('@@ valid plan for some domain'))
                        continue
                    ## inner loop was broken, break the outer too (either reach or blocking failure happened)
                    break

                    ## there exist a valid plan for all other outcomes (no break happened)
                    # else:
                    #     if verbose: print(fg_yellow('\n@@ valid plan for all outcomes'))

                    #     ## push the state and probabilistic actions into the self.open_stack 
                    #     ## if {(s, a) exist p | s !exist Sg, s !exist S_\pi, a is probabilistic}
                    #     ## ! currently, we assume only one probabilistic action in each state
                    #     self.push_prob_actions(policy, verbose)

                    #     ## update global policy ##
                    #     self.policy.update(policy)
                    #     # valid_plan_for_all = True

                    # ## no valid plan for other outcomes, remove path from state in policy 
                    # ## and put state and action in dead ends list
                    # if not valid_plan_for_all:
                    #     if verbose: print(fg_red('\n@@ no valid plan for all outcomes'))
                    #     self.deadend_list[state].append(Counter(self.policy[state]))
                    #     self.open_stack[state] = None
                    #     self.remove_path(state, verbose)

                else:
                    ## continue if there are valid plans at this branch of 'state' and 'step'
                    ## (the inner for-loop wasn't broken)
                    if verbose: print(fg_yellow('\n@@ valid plan for all outcomes'))

                    ## push the state and probabilistic actions into the self.open_stack 
                    ## if {(s, a) exist p | s !exist Sg, s !exist S_\pi, a is probabilistic}
                    ## ! currently, we assume only one probabilistic action in each state 
                    self.push_prob_actions(policy, verbose)

                    ## update global policy ##
                    self.policy.update(policy)
                    continue

                ## inner loop was broken, break the outer too
                ## no valid plan for other outcomes, remove path from state in policy 
                ## and put state and action in dead ends list
                if verbose: print(fg_red('\n@@ no valid plan for all outcomes'))
                self.deadend_list[state].append(Counter(self.policy[state]))
                self.open_stack[state] = None
                self.remove_path(state, verbose)
                # break

        self.planning_time = time() - self.planning_time

        ###################################################################


    def has_deadend(self, policy, verbose=False):
        ''' check whether the policy contains states and actions in the dead-ends list
        '''

        for state, step in policy.items():
            if not step == None and state in self.deadend_list:
                if Counter(step) in self.deadend_list[state]:
                    if verbose: print(fg_red('@@ dead-end state by: ' + str(step)))
                    return True
        return False


    def modify_domain(self, state, domain_pddl, domain_obj):
        ''' modify the domain_obj such that the actions in deadend_list[state] become
            inapplicable in state
            @arg state: the current state should be investigated in deadend_list
            @arg domain_obj: the current domain that should be modified
        '''

        ## make a list of excluding action signatures (these actions become inapplicable in the current state)
        ex_actions = [list(act)[0] for act in self.deadend_list[state]] ## convert back the Counter to a list

        print(ex_actions)
        domain_obj_cp = copy.deepcopy(domain_obj)
        domain_obj_cp.make_inapplicable(ex_actions, state)
        domain_pddl = domain_obj_cp.pddl()
        # del domain_obj_cp
        # domain_obj.make_inapplicable(ex_actions, state)
        # domain_pddl = domain_obj.pddl()
        print(domain_pddl)
        print(state)
        print()

        return domain_pddl, domain_obj_cp


    def push_prob_actions(self, policy, verbose=False):
        '''
        finds probabilistic actions in the given policy and push 
        them in open_stack list for expansion on their other outcomes
        [currently we only assume one probabilistic action in each state!]
        '''

        if verbose: print(fg_yellow('@ probabilistic actions:'))
        for state, step in policy.items():
            if step is not None and not state in self.policy:
                for action in step:
                    if action[0] in self.prob_actions:
                        if verbose: print(action)
                        self.open_stack[state] = step
                        # self.open_stack[state] = action


    def apply_step(self, init, step, domain=None, verbose=False):
        """
        return a state resulting from the application of actions in the step
        @arg init : the initial state that the step has to apply on it
        @arg step : a sequence of (concurrent) fully grounded actions
        @arg domain : if domain is given one state is generated from the application 
                      of the step on init, if the domain is not given, all domains are 
                      used and a list of states are genearted from the application of 
                      the step on init
        """

        if step is None:
            if verbose: print(bg_voilet('## step is None!!'))
            if domain is not None: return init
            return OrderedDict([(init, [])])

        # if the domain is given, only action signatures in step are grounded
        # based on the given domain specification
        if domain is not None:
            for action in step:
                init = init.apply(domain.ground(action))

            return init

        # else:
        # if the domain is not given, all domains are used to make ground 
        # probabilistic action signatures (note, only one domain is sufficient 
        # to make ground deterministic action signatures)
        grounded_steps = list()
        # if there is a probabilistic action in step, make ground all possible combination of actions on all domains
        if len([action for action in step if action[0] in self.prob_actions]) > 0:
            # for domain, domain_spec in self.domains.items():
            #     grounded_steps.append([domain_spec.ground(action) for action in step])
            grounded_actions = list()
            for action in step:
                grounded_action = list()
                for domain, domain_spec in self.domains.items():
                    grounded_action.append(domain_spec.ground(action))
                grounded_actions.append(grounded_action)
            ## generate all possible combination of actions
            grounded_steps = list(itertools.product(*grounded_actions))
        # otherwise, making ground on the first domain is sufficient
        else:
            # pick up the first domain object
            for domain, domain_spec in self.domains.items():
                grounded_steps.append([domain_spec.ground(action) for action in step])
                break

        states = OrderedDict()
        for grounded_step in grounded_steps:
            state = init
            del_effects = list()
            add_effects = list()
            for action in grounded_step:
                if action is not None:
                    if action.name in self.prob_actions:
                        add_effects.extend(action.add_effects)
                        del_effects.extend(action.del_effects)
                    state = state.apply(action)
            states[state] = (tuple(add_effects), tuple(del_effects))

        return states


    def policy_image(self, domain, state, plan, verbose=False):
        """
        return a policy image of the given plan from given domain and initial state 
        @arg domain : the domain object used to generate the plan 
        @arg init : the initial state of the plan
        @arg plan : the plan
        """

        if plan is None: return OrderedDict()

        policy = OrderedDict()

        for step in plan:
            policy[state] = step
            ## make full grounded specification of actions ##
            state = self.apply_step(state, step, domain, verbose)
            policy[state] = None

        return policy


    def remove_path(self, state, verbose=False):
        """
        remove all path starting from state in the policy
        """
        if state in self.policy:
            step = self.policy[state]
            del self.policy[state]
            if state in self.open_stack and not self.open_stack[state] is None:
                self.deadend_list[state].append(Counter(self.open_stack[state]))
                # self.deadend_list[state].append(Counter([self.open_stack[state]]))
                self.open_stack[state] = None
            if step == None: return
            for s in self.apply_step(state, step, verbose=verbose):
                self.remove_path(s, verbose)


    def plan(self, verbose=False):
        """
        return an ordered dict as the final plan:
        the keys represent the steps of actions in the plan,
        the values are tuples of actions to be executed and outcome conditions 
        every sequence of actions in each step is followed by pairs of 
        conditions and a level to jump. the conditions are the outcome of 
        the actions that should be achieved after their execution.
        the plan is dictionary as: 
            plan = { level : step, ...}
            step is a tuple as:
                step = (actions, outcomes)
                    - actions is a list of actions to be executed
                    - outcomes is a list of tuples as: (conditions, jump)
                    - conditions are the effects produced by actions
                    - jump is the next level to jump and execute
        e.g., 
        4 : (check_bottom_up arm2 base1 camera1) -- ((bottom_up base1) (camera_checked base1)) 5 -- ((top_up base1) (camera_checked base1)) 6
        """

        plan = OrderedDict()

        jumpto = OrderedDict()
        visited = OrderedDict()

        level = 0
        jumpto[self.problem.initial_state] = level

        while jumpto:

            # pop items as FIFO
            (state, i) = jumpto.popitem(False)
            if state not in visited:
                # keep track of visited states
                visited[state] = i

                if state not in self.policy:
                    if state.is_true(*(self.problem.goals, self.problem.num_goals)): 
                        plan[i] = 'goal'
                    else:
                        plan[i] = None
                    continue

                step = self.policy[state]

                if step == None: 
                    if state.is_true(*(self.problem.goals, self.problem.num_goals)):
                        if verbose: print(bg_green('@ Goal is achieved'))
                        plan[i] = 'goal'
                    else:
                        print(bg_red('@ Goal is not achieved!'))
                        plan[i] = None
                else:
                    states = self.apply_step(state, step, verbose=verbose)

                    next_steps = list()
                    for s, c in states.items():
                        if s in jumpto:
                            next_steps.append((c, jumpto[s]))
                        elif s in visited:
                            next_steps.append((c, visited[s]))
                            jumpto[s] = visited[s]
                        else:
                            level += 1
                            jumpto[s] = level
                            next_steps.append((c, level))

                    plan[i] = (tuple([self.domain.ground(action) for action in step]), tuple(next_steps))

        return plan


    def print_plan(self, plan=None, verbose=True, del_list_included=False):
        """
        print the plan in a more readable form
        """

        if plan == None:
            plan = self.plan(verbose)

        print(bg_yellow('@ PLAN'))

        plan_str = str()
        for level, step in plan.items():
            plan_str+= '{:2} : '.format(level)
            if step == 'goal': 
                plan_str+= fg_beige('(DONE)')
            elif step == None: 
                plan_str+= fg_voilet('None!')
            else:
                (actions, outcomes) = step
                plan_str+= '{}'.format(' '.join(map(str, actions)))
                for (conditions, jump) in outcomes:
                    # unfold conditions as add and delete lists
                    # if there is non-deterministic outcomes
                    if len(conditions) > 0: 
                        (add_list, del_list) = conditions
                        # if there is non-deterministic delete list in outcomes
                        if del_list_included and len(del_list) > 0:
                            plan_str+= fg_yellow(' -- ({})({}) {}'.format( \
                                    ' '.join(['({0})'.format(' '.join(map(str, c))) for c in add_list]), \
                                    ' '.join(['({0})'.format(' '.join(map(str, c))) for c in del_list]), \
                                    fg_voilet(str(jump))))
                        # otherwise, exclude delete list in the representation of the plan
                        else:
                            plan_str+= fg_yellow(' -- ({}) {}'.format( \
                                    ' '.join(['({0})'.format(' '.join(map(str, c))) for c in add_list]), \
                                    fg_voilet(str(jump))))
                    else:
                        plan_str+= fg_yellow(' -- () {}'.format(fg_voilet(str(jump))))
            plan_str+= '\n'
        print(plan_str)


    def get_paths(self, plan=None, verbose=True):
        '''
            the first path starts from the root to a leaf in (pre-order),
            !HOWEVER! the next paths start from the branches in the policy

            e.g., 
            if a policy looks like this:
            0
            |
            1
           / \
          G   2
             / \
            3   4
            |   |
            G   G
            then the paths generated are:
            1) 0, 1, G
            2) 1, 2, 3, G
            3) 2, 4, G
        '''


        if plan == None:
            plan = self.plan(verbose)

        if plan[0] == None: return list()

        paths = list()

        ## store nodes and outcomes to visit
        stack = list() # each element is: (level, step)
        visited = list()

        ## push outcomes of the root into the stack in reverse order
        for i in range( len(list(plan.items())[0][1][1])-1, -1, -1 ):
            stack.append([0, list(plan.items())[0][1][1][i][1]])

        ## simulate the plan
        while True:

            if not stack: 
                break

            (level, outcome) = stack.pop()
            visited.append((level, outcome))

            if plan[level] == 'goal' or plan[level] == None:
                continue

            path = list()

            ## add the current step into the path (as its root)
            (actions, outcomes) = plan[level]
            ## include only the target outcome as requested in 'outcome'
            for (cnd, jmp) in outcomes:
                if outcome == jmp:
                    path.append((level, (actions, (cnd, jmp))))
                    break
            ## start from the next outcome of this step
            level = outcome

            ## extract a path
            while True:

                step = plan[level]

                if step == 'goal' or step == None:
                    break
                else:
                    ## unfold step into a tuple of actions and outcomes
                    (actions, outcomes) = step

                    path.append((level, (actions, outcomes[0])))

                    ## push other outcomes (except the first one) of 'step' into the stack in reverse order
                    for i in range( len(outcomes)-1, 0, -1):
                        if not (level, outcomes[i][1]) in visited:
                            stack.append([level, outcomes[i][1]])

                    ## update 'level' by the first outcome (move forward in pre-order)
                    level = outcomes[0][1]

            paths.append(path)

        return paths


    def print_paths(self, paths=None, verbose=True, del_list_included=False):
        """
        print the paths of plan in a more readable form
        """

        if paths == None:
            paths = self.get_paths(verbose=verbose)

        if paths == list(): return

        print(bg_yellow('@ subpaths'))

        p = 1
        for path in paths:
            print(fg_yellow('path{0}'.format(str(p))))
            p += 1
            plan_str = str()
            for (level, step) in path:
                plan_str+= '{:2} : '.format(level)
                if step == 'goal': 
                    plan_str+= fg_beige('(DONE)')
                elif step == None: 
                    plan_str+= fg_voilet('None!')
                else:
                    (actions, outcomes) = step
                    plan_str+= '{}'.format(' '.join(map(str, actions)))
                    (conditions, jump) = outcomes
                    # unfold conditions as add and delete lists
                    # if there is non-deterministic outcomes
                    if len(conditions) > 0: 
                        (add_list, del_list) = conditions
                        # if there is non-deterministic delete list in outcomes
                        if del_list_included and len(del_list) > 0:
                            plan_str+= fg_yellow(' -- ({})({}) {}'.format( \
                                    ' '.join(['({0})'.format(' '.join(map(str, c))) for c in add_list]), \
                                    ' '.join(['({0})'.format(' '.join(map(str, c))) for c in del_list]), \
                                    fg_voilet(str(jump))))
                        # otherwise, exclude delete list in the representation of the plan
                        else:
                            plan_str+= fg_yellow(' -- ({}) {}'.format( \
                                    ' '.join(['({0})'.format(' '.join(map(str, c))) for c in add_list]), \
                                    fg_voilet(str(jump))))
                    else:
                        plan_str+= fg_yellow(' -- () {}'.format(fg_voilet(str(jump))))
                plan_str+= '\n'
            print(plan_str)


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


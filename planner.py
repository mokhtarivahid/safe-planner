
import os, sys
from collections import OrderedDict, defaultdict, Counter
from time import time

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
                problm_pddl = self.problem.to_pddl(state)

                policy = OrderedDict()

                for domain, domain_spec in self.domains.items():

                    ## print out some info
                    if verbose:
                        print(fg_yellow('@ domain:'), domain)
                        print(fg_yellow('@ problem:'), problm_pddl)

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
                        continue

                    ## there exists a valid plan: terminate the loop ##
                    break


                ## push the state and probabilistic actions into the self.open_stack 
                ## if {(s, a) ∈ p | s !∈ Sg, s !∈ Sπ, a is probabilistic}
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

                valid_plan_for_all = False

                policy = OrderedDict()

                ## for every other outcome of 'action' look for if there is a valid plan ##
                for domain, domain_spec in self.domains.items():

                    ## generate a new state and then make plan ##
                    ## update step by replacing 'other_outcome' action with an old outcome
                    ## !! currently we only assume one probabilistic action in a state

                    try:
                        new_state = self.apply_step(state, self.policy[state], domain_spec, verbose=verbose)
                    except:
                        print(fg_red("@@ other outcome '{0}' is not applicable!!".format(str(self.policy[state]))))
                        exit()

                    if new_state in self.policy:
                        if verbose: print(fg_red('@@ new state is already visited!'))
                        continue

                    # if new_state is itself a goal state (then the plan is empty)
                    if new_state.is_true(*(self.problem.goals, self.problem.num_goals)): 
                        policy[new_state] = None
                        if verbose: print(fg_yellow('@@ new state already contains the goal!'))
                        continue

                    # in some small problems, the state may become empty by the action application
                    if new_state.is_empty():
                        if verbose: print(fg_red('@@ new state becomes empty!'))
                        break

                    ## create a pddl problem of 'new_state' as its initial state ##
                    problm_pddl = self.problem.to_pddl(new_state)

                    ## print out some info
                    if verbose:
                        print(fg_yellow('@ domain:'), domain)
                        print(fg_yellow('@ problem:'), problm_pddl)

                    plan = call_planner(domain, problm_pddl, self.planner, verbose)

                    self.planning_call += 1

                    ## if no plan exists :- dead ends ##
                    if plan == None:
                        if verbose: print(fg_red('@@ no plan exists'))
                        break

                    policy.update(self.policy_image(domain_spec, new_state, plan, verbose))

                    ## check if the plan contains states and actions in the dead-ends list ##
                    if self.has_deadend(policy, verbose):
                        policy = OrderedDict()
                        break

                ## there exist a valid plan for all other outcomes (no break happened)
                else:
                    if verbose: print(fg_yellow('\n@@ valid plan for all outcomes'))

                    ## push the state and probabilistic actions into the self.open_stack 
                    ## if {(s, a) ∈ p | s !∈ Sg, s !∈ Sπ, a is probabilistic}
                    ## ! currently, we assume only one probabilistic action in each state
                    self.push_prob_actions(policy, verbose)

                    ## update global policy ##
                    self.policy.update(policy)
                    valid_plan_for_all = True

                ## no valid plan for other outcomes, remove path from state in policy 
                ## and put state and action in dead ends list
                if not valid_plan_for_all:
                    if verbose: print(fg_red('\n@@ no valid plan for all outcomes'))
                    self.deadend_list[state].append(Counter(self.policy[state]))
                    self.open_stack[state] = None
                    self.remove_path(state, verbose)

        self.planning_time = time() - self.planning_time

        ###################################################################


    def has_deadend(self, policy, verbose=False):
        ''' check whether the policy contains states and actions in the dead-ends list
        '''

        for state, step in policy.items():
            if not step == None and state in self.deadend_list:
                if Counter(step) in self.deadend_list[state]:
                    if verbose: print(fg_red('@@ dead-end state by: ', str(step)))
                    return True
        return False


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
                        self.open_stack[state] = action


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
            for domain, domain_spec in self.domains.items():
                grounded_steps.append([domain_spec.ground(action) for action in step])
        # otherwise, making ground on the first domain is sufficient
        else:
            # pick up the first domain object
            for domain, domain_spec in self.domains.items():
                grounded_steps.append([domain_spec.ground(action) for action in step])
                break

        states = OrderedDict()
        for grounded_step in grounded_steps:
            state = init
            add_effects = list()
            for action in grounded_step:
                if action is not None:
                    if action.name in self.prob_actions:
                        add_effects = action.add_effects #+ [(-1, d) for d in action.del_effects]
                    state = state.apply(action)
            states[state] = add_effects

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
        every step takes the following form:
        level : actions -- (conditions1) level1 -- (conditions2) level2 -- and so on
        e.g., 
        4 : (check_bottom_up arm2 base1 camera1) -- ((bottom_up base1) (camera_checked base1)) 5 -- ((top_up base1) (camera_checked base1)) 6
        """

        plan = OrderedDict()

        queue = OrderedDict()
        visited = OrderedDict()

        level = 0
        queue[self.problem.initial_state] = level

        while queue:

            # pop items as in FIFO
            (state, i) = queue.popitem(False)
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
                        print(bg_green('@ Goal is achieved'))
                        plan[i] = 'goal'
                    else:
                        print(bg_red('@ Goal is not achieved!'))
                        plan[i] = None
                else:
                    states = self.apply_step(state, step, verbose=verbose)

                    next_steps = list()
                    for s, c in states.items():
                        if s in queue:
                            next_steps.append((c, queue[s]))
                        elif s in visited:
                            next_steps.append((c, visited[s]))
                            queue[s] = visited[s]
                        else:
                            level += 1
                            queue[s] = level
                            next_steps.append((c, level))

                    plan[i] = ([self.domain.ground(action) for action in step], next_steps)

        return plan


    def print_plan(self, plan):
        """
        print the plan in a more readable form
        """
        print(bg_yellow('@ plan'))

        plan_str = str()
        for level, step in plan.items():
            plan_str+= '{:2} : '.format(level)
            if step == 'goal': 
                plan_str+= fg_beige('Goal achieved!')
            elif step == None: 
                plan_str+= fg_voilet('None!')
            else:
                (actions, conditions) = step
                plan_str+= '{}'.format(' '.join(map(str, actions)))
                for (case, jump) in conditions:
                    plan_str+= fg_yellow(' -- ({}) {}'.format(' '.join(['({0})'.format(' '.join(map(str, c))) for c in case]), fg_voilet(str(jump))))
            plan_str+= '\n'
        print(plan_str)


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


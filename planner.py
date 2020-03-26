#!/usr/bin/env python3

from collections import OrderedDict, defaultdict, Counter
import os, time
from inspect import currentframe, getframeinfo

from color import fg_green, fg_red, fg_red2, fg_yellow, fg_yellow2, fg_blue, fg_voilet, fg_beige, bg_green, bg_red, bg_yellow, bg_blue, bg_voilet
from pddlparser import PDDLParser
from external_planner import call_planner
from pddl import pddl, to_pddl
from compilation import compile

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
            print(fg_red("\n[pddl parser does not support '{0}'!]\n".format(domain)))

        ## a dictionary of deterministic domains: keys as paths to pddl 
        ## domains and values as domain objects -- dict({pddl:object})
        self.domains = OrderedDict()

        ## list of the probabilistic actions names
        self.prob_actions = list()

        ## the working directory if the domain is probabilistic
        self.working_dir = None

        ## if the domain is probabilistic
        if ":probabilistic-effects" in self.domain.requirements:

            ## compile and records the given non-deterministic domain into a list of deterministic domains
            if verbose: print(fg_green('\n[Compilation to non-deterministic domains]'))
            self.working_dir = compile(domain, verbose=verbose)

            ## parse deterministic pddl domains
            for domain in sorted(listdir_fullpath(self.working_dir)):
                ## read the probabilistic actions names
                if domain.endswith('.prob'):
                    with open(domain) as f:
                        self.prob_actions = f.read().splitlines()
                ## read the deterministic domains
                if domain.endswith('.pddl'):
                    self.domains[domain] = PDDLParser.parse(domain)
        else:
            self.domains[domain] = self.domain

        ## parse pddl problem
        self.problem = PDDLParser.parse(problem)

        ## merge constants and objects
        if self.domain.constants:
            self.problem.objects = mergeDict(self.problem.objects, self.domain.constants)
            self.problem.initial_state.objects = self.problem.objects

        ## stores the external planner
        self.planner = planner

        self.policy = OrderedDict()

        ## stores states and probabilistic steps which are not yet explored ##
        self.open_terminal_states = OrderedDict({self.problem.initial_state: None})

        ## stores states and domains which lead to dead-ends (unsolvable states) ##
        self.unsolvable_states = defaultdict(set)

        self.planning_call = 0

        self.deadends_call = 0
        self.unsolvable_call = 0

        self.planning_time = time.time()

        # if new_state is itself a goal state (then the plan is empty)
        if self.problem.initial_state.is_true(self.problem.goals):
            self.policy[self.problem.initial_state] = None
            if verbose: print(fg_yellow('[Initial state already contains the goal!]'))
            return

        ##
        ## main loop of the planner
        ##
        while self.open_terminal_states:

            # pop items as in LIFO
            (state, step) = self.open_terminal_states.popitem()

            ###################################################################
            if step == None:
                if verbose: print(fg_green('\n[Make initial plan at state {}]').format(\
                            list(self.policy).index(state) if state in self.policy else 0))

                policy = self.explore_plan(state, verbose=verbose)

                if not policy:
                    ## if no such domain nor plan exist ##
                    if verbose: print(fg_red2('  -- no initial plan found!'))
                    ## put in the self.unsolvable_states all states leading to 'state' and remove their path from self.policy ##
                    for (s, stp) in [(s, stp) for (s, stp) in self.policy.items() \
                                              if stp is not None and stp[0] is not None \
                                              and state in self.apply_step(s, stp[0], verbose=verbose)]:
                        self.unsolvable_states[s].add(stp[1])
                        if verbose: print(fg_red2('  -- unsolvable by \'{}\''.format(os.path.basename(stp[1]))))
                        self.remove_path(s, verbose=False)
                        self.open_terminal_states[s] = None

                else:
                    ## update global policy ##
                    # self.policy.update(policy)
                    self.policy = self.update_policy(self.policy, policy, verbose=verbose)

                    ## push the state and probabilistic actions into the self.open_terminal_states 
                    ## if {(s, a) exist p | s !exist Sg, s !exist S_\pi, a is probabilistic}
                    self.push_open_terminal_states(verbose)

                ## continue the main while-loop and do not run the following code
                continue

            ###################################################################
            ## if step == None: ##
            else:
                policies = OrderedDict()

                ## make all possible states from application of 'step' in 'state'
                new_states = self.apply_step(state, step, verbose=verbose)

                if verbose: print(fg_green('\n[Expand \'{}\' -- {} possible states]').format(\
                            ' '.join([str('('+' '.join(s)+')') for s in step]), len(new_states)))

                # if verbose: print(fg_yellow('[{} states to expand]'.format(len(new_states))))

                for (new_state, res) in new_states.items():

                    if verbose: print(fg_yellow2('  -- state {}'.format((list(new_states).index(new_state)))))

                    # if new_state is itself a goal state (then the plan is empty)
                    if new_state.is_true(self.problem.goals): 
                        policies[new_state] = None
                        if verbose: print(fg_yellow('    -- already contains the goal'))
                        continue

                    # in some small problems, the state may become empty by the step application
                    if new_state.is_empty():
                        if verbose: print(fg_red('    -- empty state by \'{}\'!'.format(os.path.basename(res[0][1]))))
                        break

                    if new_state in self.policy:
                        if verbose: print(fg_yellow('    -- already visited'))
                        continue

                    policy = self.explore_plan(new_state, verbose=verbose)

                    if not policy:
                        break
                    else:
                        if verbose: print(fg_yellow('    -- there is a valid plan'))
                        # policies.update(policy)
                        policies = self.update_policy(policies, policy, verbose=verbose)
                        continue

                else:
                    ## continue if there are valid plans at this branch of 'state' and 'step'
                    ## (the inner for-loop wasn't broken)
                    if verbose: print(fg_yellow('  -- all states are solvable'))

                    ## update global policy and continue the main loop ##
                    # self.policy.update(policies)
                    self.policy = self.update_policy(self.policy, policies, verbose=verbose)

                    ## push the state and probabilistic actions into the self.open_terminal_states 
                    ## if {(s, a) exist p | s !exist Sg, s !exist S_\pi, a is probabilistic}
                    self.push_open_terminal_states(verbose)

                    ## skip running the rest code and continue the main while loop
                    continue

                ## there were not valid plans for all possible outcomes of 'state' and 'step',
                ## (i.e., some break happened in the above for-loop)
                ## no valid plan for other outcomes, remove path from 'state' in policy 
                ## and put 'state' in self.unsolvable_states
                if verbose: print(fg_red2('  -- some states are unsolvable'))
                self.unsolvable_states[state].add(self.policy[state][1])
                if verbose: print(fg_red2('-- \'{}\' added unsolvable by \'{}\''.format(' '.join([str('('+' '.join(s)+')') for s in step]),os.path.basename(self.policy[state][1]))))
                self.remove_path(state, verbose=False)
                self.open_terminal_states[state] = None

        self.planning_time = time.time() - self.planning_time
        print('')

        ###################################################################

    def explore_plan(self, state, deep=False, verbose=False):
        '''
        extend the policy and make a plan from the given state
        @arg state : a given state that a plan is made on it
        @arg deep : if False, a plan from the first applicable 
                    domain on @state is returned;
                    if True, all applicable domains on @state are 
                    tried and the aggregated policy is returned 
        '''

        ## create a pddl problem given retrieved 'state' as its initial state ##
        problm_pddl = pddl(self.problem, state=state, path=self.working_dir)

        if verbose: print(fg_yellow2('    -- problem:') + problm_pddl)

        policy = OrderedDict()

        for domain, domain_spec in self.domains.items():

            if domain in self.unsolvable_states[state]:
                if verbose: print(fg_red('      -- already unsolvable by \'{}\''.format(os.path.basename(domain))))
                self.unsolvable_call += 1
                continue

            if verbose: print(fg_yellow2('    -- domain:') + domain)

            plan = call_planner(domain, problm_pddl, self.planner, verbose)

            if verbose == 1: print_classical_plan(plan)

            self.planning_call += 1

            ## if no plan exists try the next domain ##
            if plan == None:
                if verbose: print(fg_red('      -- no plan found - added unsolvable by \'{}\''.format(os.path.basename(domain))))
                self.unsolvable_states[state].add(domain)
                continue

            ## there exists a valid plan: terminate the loop ##
            if not deep: return self.policy_image(domain, domain_spec, state, plan, verbose)

            # policy.update(self.policy_image(domain, domain_spec, state, plan, verbose))
            policy = self.update_policy(policy, self.policy_image(domain, domain_spec, state, plan, verbose), verbose=verbose)

        ## no plan exists
        return policy


    # def push_open_terminal_states(self, policy, verbose=False):
    #     '''
    #     finds non-deterministic actions in the given policy and push 
    #     them in open_terminal_states for expansion on their other outcomes
    #     '''
    #     nd_actions = list()
    #     for state, step in policy.items():
    #         if step is not None: # and not state in self.policy:
    #             for action in step[0]:
    #                 if action[0] in self.prob_actions:
    #                     self.open_terminal_states[state] = step[0]
    #                     nd_actions.append(action)
    #     if verbose and nd_actions: 
    #         print(fg_yellow('[non-deterministic actions to further expand: ')+\
    #             '{}'.format(' '.join(map(str, nd_actions)))+fg_yellow(']'))


    def push_open_terminal_states(self, verbose=False):
        '''
        finds non-goal terminal states in self.policy and push them in 
        self.open_terminal_states for expansion on their other outcomes
        '''
        for state, step in self.policy.items():
            if step is not None:
                new_states = self.apply_step(state, step[0], verbose=verbose)
                for new_state in new_states:
                    if not new_state in self.policy and not new_state.is_true(self.problem.goals):
                        self.open_terminal_states[state] = step[0]
                        break
        if verbose and self.open_terminal_states.values():
            print(fg_yellow('  -- non-deterministic steps to expand: ')+\
                '{}'.format((' '.join([' '.join([str('('+' '.join(s)+')') for s in step]) \
                    for step in self.open_terminal_states.values() if step is not None]))))


    def update_policy(self, policy1, policy2, preserve=True, verbose=False):
        '''
        update policy1 by policy2 but skips already existed items
        @arg policy1 : the main given and the output policy
        @arg policy2 : the given policy to be merged into @policy1
        @arg preserve : if True, preserve old values in policy1 (i.e., 
                        do not update the old values if any exists)
        '''
        for state, step in policy2.items():
            if state not in policy1:
                policy1[state] = step
            elif not preserve:
                policy1[state] = step
        return policy1


    def policy_image(self, domain, domain_spec, state, plan, verbose=False):
        """
        return a policy image of the given plan from given domain and initial state 
        @arg domain : the domain object used to generate the plan 
        @arg init : the initial state of the plan
        @arg plan : the plan
        """
        if plan is None: return OrderedDict()

        policy = OrderedDict()

        for step in plan:
            policy[state] = (step, domain)
            ## make full grounded specification of actions ##
            state = self.apply_step(state, step, domain_spec, verbose)
            policy[state] = None

        return policy


    def remove_path(self, state, verbose=False):
        """
        remove all path starting from state in the policy
        """
        if state in self.open_terminal_states:
            if verbose and self.open_terminal_states[state] is not None: 
                print(fg_yellow('  -- removed from open_terminal_states: ')+\
                    str(self.open_terminal_states[state]))
            del self.open_terminal_states[state]
        if state in self.policy:
            step = self.policy[state]
            if verbose and step is not None: 
                print(fg_yellow(' -- removed from policy: ')+str(step))
            del self.policy[state]
            if step == None: return
            for s in self.apply_step(state, step[0], verbose=verbose):
                ## exclude states that in some domains a non-deterministic action 
                ## leads to the previous state (before action application)
                if s in self.policy and self.policy[s] is not None and \
                    not state in self.apply_step(s, self.policy[s][0], verbose=verbose):
                    self.remove_path(s, verbose)


    def apply_step(self, init, step, domain=None, verbose=False):
        """
        return a state resulting from the application of actions in the step
        @arg init : the initial state that the step has to apply on it
        @arg step : a sequence of (concurrent) fully grounded actions
        @arg domain : if domain is given one state is generated from the application 
                      of the step on init, if the domain is not given, all domains are 
                      used and a list of states are generated from the application of 
                      the step on init
        """
        if step is None:
            if verbose: print(fg_voilet('    -- step is None!!'))
            if domain is not None: return init
            return OrderedDict([(init, [])])

        # if the domain is given, only action signatures in step are grounded
        # based on the given domain specification
        if domain is not None:
            for action in step:
                init = init.apply(domain.ground(action))
            return init

        states = OrderedDict()

        # if there is not probabilistic actions in step, making ground on the first domain is sufficient
        if len([action for action in step if action[0] in self.prob_actions]) == 0:
            for domain, domain_spec in self.domains.items():
                state = init
                for action in step:
                    grounded_action = domain_spec.ground(action)
                    state = state.apply(grounded_action)
                states[state] = [((), domain)]
                return states
        
        # otherwise, if there is a probabilistic action in step, 
        # make ground the given step on all domains
        for domain, domain_spec in self.domains.items():
            state = init
            del_effects = set()
            add_effects = set()
            for action in step:
                grounded_action = domain_spec.ground(action)
                # if grounded_action is not None:
                ## effects of the probabilistic actions are included for the purpose of final plan generation
                if grounded_action.name in self.prob_actions:
                    add_effects |= set(grounded_action.add_effects)
                    del_effects |= set(grounded_action.del_effects)
                state = state.apply(grounded_action)
            if not state in states:
                states[state] = [((add_effects, del_effects), domain)]
            elif not (add_effects, del_effects) in [eff for (eff, _) in states[state]]:
                states[state].append(((add_effects, del_effects), domain))
                # if verbose: print(fg_red('non-deterministic effects generate a similar state'), states[state])

        return states


    def plan(self, tree=False, verbose=False):
        """
        return an ordered dict as the final plan:
        the keys represent the steps of actions in the plan,
        the values are tuples of actions to be executed and outcome conditions 
        every sequence of actions in each step is followed by pairs of 
        conditions and a level to jump. the conditions are the outcome of 
        the actions that should be achieved after their execution.
        @arg tree : if True, plan is tree like. it will include goal states as a jump point in the plan
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
                    if state.is_true(self.problem.goals): 
                        plan[i] = 'GOAL'
                    else:
                        plan[i] = None
                    continue

                step = self.policy[state]

                if step == None: 
                    if state.is_true(self.problem.goals):
                        # if verbose: print(fg_green('[Goal is achieved]'))
                        plan[i] = 'GOAL'
                    else:
                        if verbose: print(bg_red('[Goal is not achieved!]'))
                        plan[i] = None
                else:
                    states = self.apply_step(state, step[0], verbose=verbose)

                    next_steps = list()
                    for s, cnd in states.items():
                        for c in cnd:
                            if s in jumpto:
                                next_steps.append((c[0], jumpto[s]))
                            elif s in visited:
                                next_steps.append((c[0], visited[s]))
                                jumpto[s] = visited[s]
                            else:
                                if not tree and s.is_true(self.problem.goals): 
                                    jumpto[s] = 'GOAL'
                                    next_steps.append((c[0], 'GOAL'))
                                else:
                                    level += 1
                                    jumpto[s] = level
                                    next_steps.append((c[0], level))

                    plan[i] = (tuple([self.domain.ground(action) for action in step[0]]), tuple(next_steps))

        return plan


    def print_plan(self, plan=None, del_effects_included=False, verbose=True):
        """
        print the plan in a more readable form
        """
        if plan == None:
            plan = self.plan(verbose)

        print(bg_yellow('@ PLAN'))

        plan_str = str()
        for level, step in plan.items():
            if level == 'GOAL': continue
            plan_str+= '{:2} : '.format(level)
            if step == 'GOAL': 
                plan_str+= fg_beige('GOAL')
            elif step == None: 
                plan_str+= fg_voilet('None!')
            else:
                (actions, outcomes) = step
                plan_str+= '{}'.format(' '.join(map(str, actions)))
                for (conditions, jump) in outcomes:
                    ## represent jump in different color
                    jump_str = fg_voilet(str(jump))  # voile if there is a jump
                    if jump == 'GOAL': jump_str =fg_beige(str(jump))  # beige if it is a goal

                    # unfold conditions as add and delete lists
                    # if there is non-deterministic outcomes
                    if len(conditions) > 0: 
                        (add_list, del_list) = conditions
                        # if there is non-deterministic delete list in outcomes
                        if del_effects_included and len(del_list) > 0:
                            plan_str+= fg_yellow(' -- ({})({}) {}'.format( \
                                    ' '.join(['({0})'.format(' '.join(map(str, c))) for c in add_list]), \
                                    ' '.join(['({0})'.format(' '.join(map(str, c))) for c in del_list]), \
                                    jump_str))
                        # otherwise, exclude delete list in the representation of the plan
                        else:
                            plan_str+= fg_yellow(' -- ({}) {}'.format( \
                                    ' '.join(['({0})'.format(' '.join(map(str, c))) for c in add_list]), \
                                    jump_str))
                    else:
                        plan_str+= fg_yellow(' -- () {}'.format(jump_str))
            plan_str+= '\n'
        print(plan_str)


    def get_paths(self, plan=None, verbose=True):
        '''
            the first path starts from the root to a leaf in pre-ordering,
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

        if plan[0] == 'GOAL': return list()

        if plan[0] == None: return list()

        paths = list()

        ## store nodes and outcomes to visit
        stack = list() # each element is: (level, step)
        visited = list()

        ## push outcomes of the root into the stack in reverse order
        for i in range( len(list(plan.items())[0][1][1])-1, -1, -1 ):
            stack.append([0, list(plan.items())[0][1][1][i][1]])

        ## simulate the plan
        while stack:

            (level, outcome) = stack.pop()
            visited.append((level, outcome))

            if plan[level] == 'GOAL' or plan[level] == None:
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

                if step == 'GOAL' or step == None:
                    break
                else:
                    ## unfold step into a tuple of actions and outcomes
                    (actions, outcomes) = step

                    if not (level, (actions, outcomes[0])) in path:
                        path.append((level, (actions, outcomes[0])))
                    else:
                        break

                    ## push other outcomes (except the first one) of 'step' into the stack in reverse order
                    for i in range( len(outcomes)-1, 0, -1):
                        if not (level, outcomes[i][1]) in visited:
                            stack.append([level, outcomes[i][1]])

                    ## update 'level' by the first outcome (move forward in pre-order)
                    level = outcomes[0][1]

            paths.append(path)

        return paths


    def print_paths(self, plan=None, paths=None, verbose=True, del_effects_included=False):
        """
        print the paths of plan in a more readable form
        """
        if paths == None:
            paths = self.get_paths(plan, verbose=verbose)

        if paths == list(): return

        print(bg_yellow('@ SUBPATHS'))

        p = 1
        for path in paths:
            print(fg_yellow('-- path{} ({})'.format(str(p), len(path))))
            p += 1
            plan_str = str()
            for (level, step) in path:
                plan_str+= '{:2} : '.format(level)
                if step == 'GOAL': 
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
                        if del_effects_included and len(del_list) > 0:
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

###############################################################################
## some functions
###############################################################################

def listdir_fullpath(directory):
    '''create and return a list of paths to all files in directory'''
    return [os.path.join(directory, file) for file in os.listdir(directory)]

def mergeDict(dict1, dict2):
    ''' merge dictionaries as well as merge values of common keys'''
    dict3 = dict1
    for key in dict3:
        if key in dict2:
            dict3[key] = tuple(list(set(dict3[key]) | set(dict2[key])))
    return dict3

def get_linenumber():
    frameinfo = getframeinfo(currentframe())
    return (frameinfo.filename.split('/')[-1], frameinfo.lineno)

def print_classical_plan(plan):
    '''print out given plan in a readable format'''
    if plan is None: return
    print(fg_yellow2('    -- plan:'))
    for step in plan:
        print('            '+' '.join([str('('+' '.join(action)+')') for action in step]))

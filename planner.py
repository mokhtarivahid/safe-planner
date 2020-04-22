#!/usr/bin/env python3

from collections import OrderedDict, Counter, defaultdict
import os, time
from inspect import currentframe, getframeinfo
from itertools import product
import logging
import copy 

from color import fg_green, fg_red, fg_red2, fg_yellow, fg_yellow2, fg_blue, fg_voilet, fg_beige, bg_green, bg_red, bg_yellow, bg_blue, bg_voilet
from pddlparser import PDDLParser
from external_planner import call_planner
from pddl import pddl, to_pddl
from compilation import compile
from problem import State
from domain import Domain

logging.basicConfig(level=logging.DEBUG,
                    format='(%(filename)s:%(lineno)s - %(funcName)s) %(message)s')


class Planner(object):

    def __init__(self, domain, problem, planner='ff', verbose=False):
        """
        @arg domain : path to pddl domain (string)
        @arg problem : path to pddl problem (string)
        @arg planner : name of the external planner (string)
        @arg planner : name of the external planner (string)
        @arg verbose : if True, prints out statistics 
        """
        # store the given verbosity
        self.verbose = verbose

        if problem is None:
            # parse pddl domain and problem together in a single file
            self.domain, self.problem = PDDLParser.parse(domain)
        else:
            # parse pddl non-deterministic domain 
            self.domain = PDDLParser.parse(domain)

            # parse pddl problem
            self.problem = PDDLParser.parse(problem)

        # store domain and problem files paths
        self.problem_file = problem
        self.domain_file = domain

        # a dictionary of deterministic domains: keys as paths to deterministic domains 
        # files and values as domain objects -- dict({pddl:object})
        self.domains = OrderedDict()

        # a list of the names of non-deterministic actions
        self.prob_actions = list()

        # the working directory if the domain is non-deterministic
        self.working_dir = None

        # if the domain is non-deterministic/probabilistic
        if ":probabilistic-effects" in self.domain.requirements:

            # compile and records the given non-deterministic domain into a list of deterministic domains
            if self.verbose: print(fg_green('\n[Compilation to non-deterministic domains]'))
            self.working_dir = compile(self.domain, verbose=verbose)

            # parse pddl deterministic domains
            for domain in sorted(listdir_fullpath(self.working_dir)):
                # read the names of non-deterministic actions
                if domain.endswith('.prob'):
                    with open(domain) as f:
                        self.prob_actions = f.read().splitlines()
                # parse the deterministic domains
                if domain.endswith('.pddl'):
                    self.domains[domain] = PDDLParser.parse(domain)
        else:
            self.domains[domain] = self.domain

        # merge constants and objects (if any exists)
        if self.domain.constants:
            self.problem.initial_state.objects = mergeDict(self.problem.initial_state.objects, self.domain.constants)

        # store the name of external classical planner
        self.planner = planner

        # the resulting policy as an ordered dictionary 
        # -- keys as states and values as actions applicable in the associated states
        self.policy = OrderedDict()

        # store states and actions leading to unsolvable (dead-ends) states
        self.unsolvable_states = defaultdict(set)

        # total number of calls to external planner
        self.planning_call = 0

        # total number of seen unsolvable states
        self.unsolvable_call = 0

        # planning time
        self.planning_time = 0.0

        # if the initial state already contains the goal (then the plan is empty)
        if self.problem.initial_state.is_true(self.problem.goals):
            self.policy[self.problem.initial_state] = None
            if self.verbose: print(fg_yellow('[Initial state already contains the goal!]'))
            return

        self.planning_time = time.time()

        ##
        ## main loop of the planner
        ##
        while True:
            # find a non-goal terminal state in the current policy
            state = self.find_open_terminal_state()

            # if no non-goal terminal state exists then return the current policy and finish the loop
            if state is None: 
                break

            # find a plan at the current state
            policy = self.find_plan(state)

            # if a policy is found then merge it into the resulting self.policy
            if policy is not None:
                self.policy = self.update_policy(self.policy, policy)

            # if no plan found at the initial state then no policy exists and finish the loop
            elif state == self.problem.initial_state:
                break

            else:
                if self.verbose: print(fg_red2('  -- no initial plan found!'))
                # put in the self.unsolvable_states all states leading to 'state' and remove their path from self.policy
                for (s, step) in [(s, step) for (s, step) in self.policy.items() if step is not None \
                        and state in self.apply_step(init=s, step=step, verbose=verbose)]:
                    if self.unsolvable_states[s] is not None:
                        self.unsolvable_states[s].update(set(step))
                    if self.verbose: print(fg_red2('  -- unsolvable by: {}'.format(\
                        ' '.join([str('('+' '.join(a)+')') for a in step]))))
                    self.remove_path(s)

                self.unsolvable_states[state] = None

        self.planning_time = time.time() - self.planning_time
        print('')

        ###################################################################

    def find_plan(self, init, verbose=False):
        '''
        extend the policy and make a plan from the given state
        @arg state : a given state that a plan is made on it
        @arg deep : if False, a plan from the first applicable 
                    domain on @state is returned;
                    if True, all applicable domains on @state are 
                    tried and the aggregated policy is returned 
        '''
        # in some small problems, the state may become empty by the step application
        if not init:
            if self.verbose: print(fg_red('    -- empty state!'))
            return None

        if init in self.unsolvable_states:
            self.unsolvable_call += 1
            if self.unsolvable_states[init] is None:
                if self.verbose: print(fg_red('      -- already unsolvable state'))
                return None
            if self.verbose: print(fg_red('      -- already unsolvable by: {}'.format(\
                ' '.join([str('('+' '.join(a)+')') for a in self.unsolvable_states[init]]))))

        state = init
        policy = OrderedDict()
        policy[state] = None

        while True:

            if state.is_true(self.problem.goals):
                return policy

            # modify state such that plan does not start with an action in self.unsolvable_states[state]
            # create a pddl problem given retrieved 'state' as its initial state 
            problem_pddl = pddl(self.problem, \
                state=state.constrain_state(self.unsolvable_states[state]), \
                path=self.working_dir)

            for domain_pddl, domain_obj in self.domains.items():
                # modify domain such that plan does not start with an action in self.unsolvable_states[state]
                cons_domain_obj = domain_obj.constrain_domain(self.unsolvable_states[state])

                cons_domain_pddl = pddl(cons_domain_obj)

                if self.verbose: 
                    print(fg_yellow2('    -- problem:') + problem_pddl)
                    print(fg_yellow2('    -- domain:') + cons_domain_pddl)

                plan = call_planner(cons_domain_pddl, problem_pddl, self.planner, verbose=verbose)

                self.planning_call += 1

                if verbose == 1: print_classical_plan(plan)

                # if no plan exists try the next domain
                if plan == None:
                    if self.verbose: print(fg_red('      -- no plan found by \'{}\''.format(os.path.basename(domain_pddl))))
                    continue

                state = self.safe_policy_image(policy, domain_pddl, domain_obj, \
                        state, plan, verbose=verbose)

                break
            # for-loop didn't break, that is, no plan was found
            else: # no plan exists
                if not policy: return None
                state, step = policy.popitem()
                self.unsolvable_states[state] = None

                if not policy: return None
                state, step = policy.popitem()
                self.unsolvable_states[state].update(set(step))


    def safe_policy_image(self, policy, domain, domain_obj, state, plan, verbose=False):
        """
        return a policy image of the given plan from given domain and initial state 
        @arg domain : the domain object used to generate the plan 
        @arg init : the initial state of the plan
        @arg plan : the plan
        """
        for step in plan:
            ## make full grounded specification of actions ##
            new_state = self.apply_step(init=state, step=step, domain=domain_obj, verbose=verbose)
            if (new_state in self.unsolvable_states and \
                self.unsolvable_states[new_state] is None) \
                or new_state in policy or new_state in self.policy:
                self.unsolvable_call += 1
                self.unsolvable_states[state].update(set(step))
                if self.verbose: print(fg_red('      -- plan has already unsolvable state by: {}'.format(\
                    ' '.join([str('('+' '.join(a)+')') for a in self.unsolvable_states[state]]))))
                return state

            policy[state] = step
            policy[new_state] = None
            state = new_state

        return state

    # def find_plan(self, state, verbose=False):
    #     '''
    #     extend the policy and make a plan from the given state
    #     @arg state : a given state that a plan is made on it
    #     @arg deep : if False, a plan from the first applicable 
    #                 domain on @state is returned;
    #                 if True, all applicable domains on @state are 
    #                 tried and the aggregated policy is returned 
    #     '''
    #     # in some small problems, the state may become empty by the step application
    #     if not state:
    #         if self.verbose: print(fg_red('    -- empty state!'))
    #         return None

    #     if state in self.unsolvable_states:
    #         self.unsolvable_call += 1
    #         if self.verbose: print(fg_red('      -- already unsolvable by \'{}\''.format(self.unsolvable_states[state])))

    #     # modify state such that plan does not start with an action in self.unsolvable_states[state]
    #     # create a pddl problem given retrieved 'state' as its initial state 
    #     problem_pddl = pddl(self.problem, \
    #         state=state.constrain_state(self.unsolvable_states[state]), \
    #         path=self.working_dir)

    #     policy = OrderedDict()

    #     for domain_pddl, domain_obj in self.domains.items():

    #         ## modify domain such that plan does not start with an action in self.unsolvable_states[state]
    #         cons_domain_obj = domain_obj.constrain_domain(self.unsolvable_states[state])

    #         cons_domain_pddl = pddl(cons_domain_obj)

    #         if self.verbose: 
    #             print(fg_yellow2('    -- problem:') + problem_pddl)
    #             print(fg_yellow2('    -- domain:') + cons_domain_pddl)

    #         plan = call_planner(cons_domain_pddl, problem_pddl, self.planner, verbose=verbose)

    #         self.planning_call += 1

    #         if verbose == 1: print_classical_plan(plan)


    #         ## if no plan exists try the next domain ##
    #         if plan == None:
    #             if self.verbose: print(fg_red('      -- no plan found by \'{}\''.format(os.path.basename(domain_pddl))))
    #             continue

    #         policy = self.policy_image(domain_pddl, domain_obj, state, plan, verbose=verbose)

    #         if self.has_unsolvable(policy, verbose=verbose):
    #             continue

    #         return policy

    #     ## no plan exists
    #     return None


    def has_unsolvable(self, policy, verbose=False):
        ''' check whether the policy contains states and actions in the dead-ends list
        '''
        for state, step in policy.items():
            if step is not None and state in self.unsolvable_states:
                if self.unsolvable_states[state] is None or \
                   set(step).issubset(self.unsolvable_states[state]):
                    if self.verbose: print(fg_red('      -- plan has already unsolvable state by: ' + \
                            ' '.join([str('('+' '.join(a)+')') for a in step])))
                    return True
        return False


    def find_open_terminal_state(self, verbose=False):
        '''finds a non-goal terminal state in self.policy and returns if for expansion'''
        for state, step in self.policy.items():
            if step is not None:
                for new_state in self.apply_step(init=state, step=step, verbose=verbose):
                    if not new_state in self.policy and not new_state.is_true(self.problem.goals):
                        if self.verbose: print(fg_yellow('  -- expand non-goal terminal state by: ')+\
                                            ' '.join([str('('+' '.join(a)+')') for a in step]))
                        return new_state
            elif not state.is_true(self.problem.goals):
                if self.verbose: print(fg_yellow('  -- expand non-goal terminal state by None'))
                return state
        if self.policy: return None
        return self.problem.initial_state 


    def update_policy(self, policy1, policy2, preserve=False, verbose=False):
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


    def policy_image(self, domain, domain_obj, state, plan, verbose=False):
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
            state = self.apply_step(init=state, step=step, domain=domain_obj, verbose=verbose)
            policy[state] = None

        return policy


    def remove_path(self, state, verbose=False):
        """
        remove all path starting from state in the policy
        """
        if state in self.policy:
            step = self.policy[state]
            if verbose and step is not None: 
                print(fg_yellow(' -- removed from policy: ') + \
                    ' '.join([str('('+' '.join(a)+')') for a in step]))
            del self.policy[state]
            if step == None: return
            for s in self.apply_step(init=state, step=step, verbose=verbose):
                ## exclude states that in some domains a non-deterministic action 
                ## leads to the previous state (the state before action application)
                if s in self.policy and self.policy[s] is not None and \
                    not state in self.apply_step(init=s, step=self.policy[s], verbose=verbose):
                    self.remove_path(s)
                elif s in self.policy and self.policy[s] is None:
                    self.remove_path(s)


    def apply_step(self, init, step, domain=None, det_effect_inc=False, verbose=False):
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
            if self.verbose: print(bg_voilet('## step is None!!'))
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
            # for domain, domain_obj in self.domains.items():
            #     grounded_steps.append([domain_obj.ground(action) for action in step])
            grounded_actions = list()
            for action in step:
                grounded_action = set()
                for domain, domain_obj in self.domains.items():
                    grounded_action.add(domain_obj.ground(action))
                grounded_actions.append(tuple(grounded_action))
            ## generate all possible combination of actions
            grounded_steps = list(product(*grounded_actions))
        # otherwise, making ground on the first domain is sufficient
        else:
            # pick up the first domain object
            for domain, domain_obj in self.domains.items():
                grounded_steps.append([domain_obj.ground(action) for action in step])
                break

        states = OrderedDict()
        for grounded_step in grounded_steps:
            state = init
            del_effects = set()
            add_effects = set()
            for grounded_action in grounded_step:
                # if grounded_action is not None:
                ## effects of the probabilistic actions are included for the purpose of final plan generation
                if (grounded_action.name in self.prob_actions) or (det_effect_inc):
                    add_effects |= set(grounded_action.effects.add_effects)
                    del_effects |= set(grounded_action.effects.del_effects)
                    for effect in grounded_action.effects.when_effects:
                        (pos_cnd_lst, neg_cnd_lst, pos_eff_lst, neg_eff_lst) = effect
                        if state.is_true(pos_cnd_lst, neg_cnd_lst):
                            add_effects |= set(pos_eff_lst)
                            del_effects |= set(neg_eff_lst)
                state = state.apply(grounded_action)
            states[state] = (add_effects, del_effects)

        return states


    # def apply_step(self, init, step, domain=None, verbose=False):
    #     """
    #     return a state resulting from the application of actions in the step
    #     @arg init : the initial state that the step has to apply on it
    #     @arg step : a sequence of (concurrent) fully grounded actions
    #     @arg domain : if domain is given one state is generated from the application 
    #                   of the step on init, if the domain is not given, all domains are 
    #                   used and a list of states are generated from the application of 
    #                   the step on init
    #     """
    #     if step is None:
    #         if self.verbose: print(fg_voilet('    -- step is None!!'))
    #         if domain is not None: return init
    #         return OrderedDict([(init, [])])

    #     # if the domain is given, only action signatures in step are grounded
    #     # based on the given domain specification
    #     if domain is not None:
    #         for action in step:
    #             init = init.apply(domain.ground(action))
    #         return init

    #     states = OrderedDict()

    #     # if there is not probabilistic actions in step, making ground on the first domain is sufficient
    #     if len([action for action in step if action[0] in self.prob_actions]) == 0:
    #         for domain, domain_obj in self.domains.items():
    #             state = init
    #             del_effects = set()
    #             add_effects = set()
    #             for action in step:
    #                 grounded_action = domain_obj.ground(action)
    #                 add_effects |= set(grounded_action.add_effects)
    #                 del_effects |= set(grounded_action.del_effects)
    #                 for effect in grounded_action.when_effects:
    #                     (pos_cnd_lst, neg_cnd_lst, pos_eff_lst, neg_eff_lst) = effect
    #                     add_effects |= set(pos_eff_lst)
    #                     del_effects |= set(neg_eff_lst)
    #                 state = state.apply(grounded_action)
    #             states[state] = [((add_effects, del_effects), domain)]
    #             # states[state] = [((), domain)]
    #             return states
        
    #     # otherwise, if there is a probabilistic action in step, 
    #     # make ground the given step on all domains
    #     for domain, domain_obj in self.domains.items():
    #         state = init
    #         del_effects = set()
    #         add_effects = set()
    #         for action in step:
    #             grounded_action = domain_obj.ground(action)
    #             # if grounded_action is not None:
    #             ## effects of the probabilistic actions are included for the purpose of final plan generation
    #             # if grounded_action.name in self.prob_actions:
    #             add_effects |= set(grounded_action.add_effects)
    #             del_effects |= set(grounded_action.del_effects)
    #             for effect in grounded_action.when_effects:
    #                 (pos_cnd_lst, neg_cnd_lst, pos_eff_lst, neg_eff_lst) = effect
    #                 add_effects |= set(pos_eff_lst)
    #                 del_effects |= set(neg_eff_lst)
    #             state = state.apply(grounded_action)
    #         if not state in states:
    #             states[state] = [((add_effects, del_effects), domain)]
    #         elif not (add_effects, del_effects) in [eff for (eff, _) in states[state]]:
    #             states[state].append(((add_effects, del_effects), domain))
    #             # if self.verbose: print(fg_red('non-deterministic effects generate a similar state'), states[state])

    #     return states


    def plan(self, tree=False, verbose=False):
        """
        return an ordered dict as the final plan:
        the keys represent the steps of actions in the plan,
        the values are tuples of actions to be executed and outcome conditions 
        every sequence of actions in each step is followed by pairs of 
        conditions and a level to jump. the conditions are the outcome of 
        the actions that should be achieved after their execution.
        @arg tree : if True, plan is tree-like. it will include goal states 
                    as jumping points in the plan
        the plan is a dictionary as: 
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
                        # if self.verbose: print(fg_green('[Goal is achieved]'))
                        plan[i] = 'GOAL'
                    else:
                        if self.verbose: print(bg_red('[Goal is not achieved!]'))
                        plan[i] = None
                else:
                    states = self.apply_step(init=state, step=step, det_effect_inc=True, verbose=verbose)

                    next_steps = list()
                    for s, c in states.items():
                        if s in jumpto:
                            next_steps.append((c, jumpto[s]))
                        elif s in visited:
                            next_steps.append((c, visited[s]))
                            jumpto[s] = visited[s]
                        else:
                            if not tree and s.is_true(self.problem.goals): 
                                jumpto[s] = 'GOAL'
                                next_steps.append((c, 'GOAL'))
                            else:
                                level += 1
                                jumpto[s] = level
                                next_steps.append((c, level))

                    plan[i] = (tuple([self.domain.ground(action) for action in step]), tuple(next_steps))

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
                    if len([action.sig for action in actions if action.sig[0] in self.prob_actions]) > 0:
                    # if len(conditions) > 0: 
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
        visited = set()

        ## push outcomes of the root into the stack in reverse order
        for i in range( len(list(plan.items())[0][1][1])-1, -1, -1 ):
            stack.append([0, list(plan.items())[0][1][1][i][1]])

        ## simulate the plan
        while stack:

            (level, outcome) = stack.pop()
            visited.add((level, outcome))

            if plan[level] == 'GOAL' or plan[level] == None:
                continue

            path = OrderedDict()

            ## add the current step into the path (as its root)
            (actions, outcomes) = plan[level]
            ## include only the target outcome as requested in 'outcome'
            for (cnd, jmp) in outcomes:
                if outcome == jmp:
                    path[level] = (actions, [(cnd, jmp)])
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

                    if not (level, (actions, [outcomes[0]])) in path.items() and \
                       not (level, outcomes[0][1]) in visited:
                        path[level] = (actions, [outcomes[0]])
                    else:
                        break

                    ## add current node (current step and its first outcome) to visited
                    visited.add((level, outcomes[0][1]))

                    ## push other outcomes (except the first one) of 'step' into the stack in reverse order
                    for i in range(len(outcomes)-1, 0, -1):
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
            for (level, step) in path.items():
                plan_str+= '{:2} : '.format(level)
                if step == 'GOAL': 
                    plan_str+= fg_beige('(DONE)')
                elif step == None: 
                    plan_str+= fg_voilet('None!')
                else:
                    (actions, outcomes) = step
                    plan_str+= '{}'.format(' '.join(map(str, actions)))
                    (conditions, jump) = outcomes[0]
                    ## represent jump in different color
                    jump_str = fg_voilet(str(jump))  # voile if there is a jump
                    if jump == 'GOAL': jump_str =fg_beige(str(jump))  # beige if it is a goal

                    # unfold conditions as add and delete lists
                    # if there is non-deterministic outcomes
                    if len([action.sig for action in actions if action.sig[0] in self.prob_actions]) > 0:
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

    def log_performance(self):
        '''stores the planner performance in a file next to given problem file'''
        # create a stat file
        import json
        performance = {'time':round(self.planning_time,3),\
                       'planning_call':self.planning_call,\
                       'unsolvable_call':self.unsolvable_call,\
                       'solvable': 'GOAL' in self.plan().keys() or\
                                   'GOAL' in self.plan().values()}
        if self.problem_file is not None:
            stat_file = '{}.stat'.format(os.path.splitext(self.problem_file)[0])
        else:
            stat_file = '{}.stat'.format(os.path.splitext(self.domain_file)[0])

        with open(stat_file, 'w') as outfile:
            json.dump(performance, outfile, indent=4)

        return stat_file

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
    for key in dict2:
        if not key in dict3:
            dict3[key] = dict2[key]
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

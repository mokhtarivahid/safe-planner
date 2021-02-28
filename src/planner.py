#!/usr/bin/env python

from collections import OrderedDict, defaultdict
import os, time, sys
from itertools import product
import json
import atexit
import signal

import color
import pddlparser
import external_planner
import pddl
import compilation

# a function to terminate running planners at exit
def cleanup(pwd, planners, verbose=0):
    from external_planner import kill_jobs
    # kill the running planners if any
    kill_jobs(pwd, planners)

    # cleanup the generated files
    if not verbose:
        try: os.system('rm -fr ' + pwd)
        except: pass
    os._exit(0)

# make sure all running planners are terminated at exit
def sig_cleanup(signum, frame):
    if signum == signal.SIGUSR1:
        sys.exit(0)


class Planner(object):

    def __init__(self, domain, problem, planners=['ff'], safe_planner=False, rank=False, alloutcome=False, verbose=False):
        '''
        @domain : path to pddl domain (string)
        @problem : path to pddl problem (string)
        @planners : a list the external planners (list of strings)
        @rank : if True, rank the compile classical planning domains
        @verbose : if True, prints out statistics 
        '''
        # store the given verbosity
        self.verbose = verbose

        if problem is None:
            # parse pddl domain and problem together in a single file
            self.domain, self.problem = pddlparser.PDDLParser.parse(domain)
        else:
            # parse pddl non-deterministic domain 
            self.domain = pddlparser.PDDLParser.parse(domain)

            # parse pddl problem
            self.problem = pddlparser.PDDLParser.parse(problem)

        # merge constants and objects (if any exists)
        if self.domain.constants:
            self.problem.initial_state.objects = mergeDict(self.problem.initial_state.objects, self.domain.constants)
            self.domain.constants.clear()

        # store domain and problem files paths
        self.problem_file = problem
        self.domain_file = domain

        # a dictionary of deterministic domains: keys as paths to deterministic domains 
        # files and values as domain objects -- dict({pddl:object})
        self.domains = OrderedDict()

        # a list of the names of all actions including new created compiled actions
        self.map_actions = OrderedDict()

        # a list of the names of non-deterministic actions
        self.prob_actions = OrderedDict()

        # the working directory if the domain is non-deterministic
        self.working_dir = None

        # compilation time
        self.compilation_time = time.time()

        # compile and records the given non-deterministic domain into a list of deterministic domains
        if self.verbose: print(color.fg_green('\n[Compilation to non-deterministic domains]'))
        self.working_dir = compilation.compile(self.domain, rank=rank, alloutcome=alloutcome, verbose=self.verbose)

        # parse pddl deterministic domains
        for domain in sorted(listdir_fullpath(self.working_dir)):
            # load the actions mapping file
            if domain.endswith('.acts'):
                with open(domain) as f:
                    self.map_actions = json.load(f)
            # read the names of non-deterministic actions
            if domain.endswith('.prob'):
                with open(domain) as f:
                    self.prob_actions = json.load(f)
            # parse the deterministic domains
            if domain.endswith('.pddl'):
                self.domains[domain] = pddlparser.PDDLParser.parse(domain)

        self.compilation_time = time.time() - self.compilation_time

        # store the list of external classical planners and assign a profile '0' to each one
        self.planners = { os.path.basename(planner).lower() : 0 for planner in planners }

        # check if the planners are available
        possible_planners = os.listdir(os.path.split(__file__)[0]+'/planners')
        for planner in self.planners:
            if planner not in map(str.lower, possible_planners):
                print(color.fg_red("\n'{0}' does not exist in 'planners/' directory!".format(planner)))
                print(color.fg_yellow("currently these planners are available: ") + str(possible_planners))
                exit()

        ## check if the domain requires derived predicates then switch to the supporting planner profile 
        ## THIS IS NOT SOUND AND MIGHT LEAD TO INACCURATE GOALS
        if len(self.domain.derived_predicates) > 0:
            for planner in list(self.planners):
                if 'ff' in planner:
                    # switch to 'ff-x'
                    del self.planners[planner]
                    self.planners['ff-x'] = 0
                elif 'fd' in planner:
                    # switch to profile 1
                    self.planners[planner] = 0

            # for planner, profile in planners.items():
            #     if profile not in args_profiles[planner]:
            #         print(color.fg_red('-- profile \'{}\' does not exist for \'{}\' planner'.format(profile,planner)))
            #         print(color.fg_yellow('-- only the following profiles exist for \'{}\':'.format(planner)))
            #         for i, args in args_profiles[planner].items():
            #             print('   {} : {}'.format(i, args))
            #         exit()

        # the resulting policy as an ordered dictionary 
        # -- keys as states and values as actions applicable in the associated states
        self.policy = OrderedDict()

        # store states and actions leading to unsolvable (dead-ends) states
        self.unsolvable_states = defaultdict(set)

        # total number of calls to external planner
        self.singleoutcome_planning_call = 0
        self.alloutcome_planning_call = 0

        # register the 'cleanup' function to make sure all running planners are terminated at exit
        atexit.register(cleanup, self.working_dir, self.planners, self.verbose)
        signal.signal(signal.SIGUSR1, sig_cleanup)

        # planning time
        self.planning_time = time.time()

        # the main loop of the planner
        if safe_planner:
            self.find_safe_policy()
        else:
            self.find_safe_policy_ndp2()

        self.planning_time = time.time() - self.planning_time
        # print('')

        # cleanup the generated files
        if self.verbose == 0:
            if not self.working_dir == None:
                try:
                    os.system('rm -fr ' + self.working_dir)
                except OSError:
                    pass

        ###################################################################


    ###################################################################
    #### safe-planner algorithm
    ###################################################################

    def find_safe_policy(self):
        '''main loop of the planner -- returns a policy if any exists'''
        # if the initial state already contains the goal (then the plan is empty)
        if self.problem.initial_state.is_true(self.problem.goals):
            self.policy[self.problem.initial_state] = None
            # verbosity
            if self.verbose: print(color.fg_yellow('[Initial state already contains the goal!]'))
            return 

        while True:

            # find a non-goal terminal state in the current policy
            state = self.find_open_terminal_state()

            if state is None and not 'GOAL' in self.plan().keys():
                print(color.fg_yellow('[unsolvable -- retry!] (%s:%s replanning) (%s unsolvable states) [%.3f s]' %\
                (self.alloutcome_planning_call, self.singleoutcome_planning_call, \
                    len(self.unsolvable_states), time.time() - self.planning_time)))
                self.policy = OrderedDict()
                state = self.problem.initial_state

            # if no non-goal terminal state exists then return the current policy and finish the for-loop
            if state is None: 
                # first refine the policy
                self.refine_policy()
                return 

            # find a plan at the current state
            policy = self.find_safe_plan(state)

            # if a policy is found then merge it into the resulting self.policy
            if policy is not None:
                self.policy = self.merge_policy(self.policy, policy)

            # if no plan found at the initial state then no policy exists and finish the loop
            elif state == self.problem.initial_state: 
                # verbosity
                if self.verbose: print(color.fg_red('\n-- no plan at the initial state %s' % u'\U0001F593'))
                # first refine the policy
                self.refine_policy()
                return 

            # otherwise; the current open terminal state is unsolvable 
            # add this state and all states leading to this state into unsolvable_states 
            # and remove those states from self.policy
            else:
                # fully unsolvable state
                self.unsolvable_states[state] = None

                # put in the self.unsolvable_states all states leading to 'state' and remove their path from self.policy
                for (s, step) in [(s, step) for (s, step) in self.policy.items() \
                        if state in self.apply_step(init=s, step=step)]:
                    # remove all states from 's' in self.policy
                    self.remove_path(s)
                    # state is partially unsolvable
                    if self.unsolvable_states[s] is not None:
                        self.unsolvable_states[s].update(set(step))
                    # verbosity
                    if self.verbose: 
                        print(color.fg_red2('  -- unsolvable by: %s %s' % (step_to_str(step), u'\U0001F593')))


    def find_safe_plan(self, state):
        '''
        extend the policy and make a plan from the given state 
        @state : a given state that a plan is made on it
        '''
        # in some small problems, the state may become empty by the step application
        if len(state) == 0:
            if self.verbose: print(color.fg_red('  -- empty state %s' % u'\U0001F593'))
            return None

        policy = OrderedDict()
        unsolvable_states = self.unsolvable_states.copy()

        while True:

            # check if the given state is already unsolvable
            if state in unsolvable_states:
                # then return failure (None) if it is fully unsolvable
                if unsolvable_states[state] is None:
                    if self.verbose: print(color.fg_red('    -- already unsolvable %s' % u'\U0001F593'))
                    return None
                # verbosity
                if self.verbose: print(color.fg_red('    -- partially unsolvable  -- excluding: %s' % step_to_str(unsolvable_states[state])))

            # increase the number of planning call
            self.alloutcome_planning_call += 1

            # verbosity: when verbosity is off: remove recorded files periodically!
            if not self.verbose:
                if self.alloutcome_planning_call > 100 and self.alloutcome_planning_call % 100 == 0:
                    try:
                        os.system('rm -fr ' + self.working_dir + '*.pddl')
                    except OSError as e:
                        print("Error: %s : %s" % (dir_path, e.strerror))

            # modify state such that plan does not start with an action in unsolvable_states[state]
            # and create a pddl problem given retrieved 'state' as its initial state 
            if state in unsolvable_states:
                problem_pddl = pddl.pddl(self.problem, \
                    state=state.constrain_state(unsolvable_states[state], self.map_actions, self.prob_actions), \
                    path=self.working_dir)
            else:
                problem_pddl = pddl.pddl(self.problem, state=state, path=self.working_dir)

            for domain_pddl, domain_obj in self.domains.items():
                # modify domain such that plan does not start with an action in unsolvable_states[state]
                if state in unsolvable_states:
                    cons_domain_obj = domain_obj.constrain_domain(unsolvable_states[state], self.map_actions, self.prob_actions)
                else:
                    cons_domain_obj = domain_obj
                # create a pddl file of the domain object
                cons_domain_pddl = pddl.pddl(cons_domain_obj, path=self.working_dir)


                if self.verbose: 
                    print(color.fg_yellow2('    -- problem:') + problem_pddl)
                    print(color.fg_yellow2('    -- domain:') + cons_domain_pddl)

                # call the external classical planner
                plan = external_planner.Plan(self.planners, cons_domain_pddl, problem_pddl, self.working_dir, verbose=self.verbose)

                # increase the number of planning call
                self.singleoutcome_planning_call += 1

                # verbosity: when verbosity is off !
                if not self.verbose:
                    if self.singleoutcome_planning_call > 0 and self.singleoutcome_planning_call % 500 == 0:
                        print(color.fg_yellow('(%s:%s replanning) (%s unsolvable states) [%.3f s]' %\
                            (self.alloutcome_planning_call, self.singleoutcome_planning_call, \
                                len(unsolvable_states), time.time() - self.planning_time)))

                # if no plan exists try the next domain
                if plan == None:
                    if self.verbose: print(color.fg_red('      -- no plan exists %s' % u'\U0001F593'))
                    continue

                # verbosity -- printout the resulting plan
                # if self.verbose == 1: print_classical_plan(plan)
                if self.verbose == 1: print(color.fg_yellow2('    -- plan:'))

                # make policy image of the plan and append it to the current policy 
                # if the plan has unsolvable states stop appending and continue planning 
                # from the last unsolvable state in the plan
                # return self.safe_policy_image(domain_pddl, domain_obj, state, plan)
                for i, step in enumerate(plan):

                    # make full grounded specification of actions and apply them in the state
                    new_state = self.apply_step(init=state, step=step, domain=domain_obj)

                    # check if the new_state is already an unsolvable state
                    # if (new_state in self.unsolvable_states and self.unsolvable_states[new_state] is None) or \
                    #    (state in self.unsolvable_states and self.unsolvable_states[state] is not None and \
                    #     set(step).issubset(self.unsolvable_states[state])):
                    if any([True for s in self.apply_step(init=state, step=step) \
                             if s in self.unsolvable_states and self.unsolvable_states[s] is None]) \
                       or (state in self.unsolvable_states and self.unsolvable_states[state] is not None and \
                           set(step).issubset(self.unsolvable_states[state])):
                        # verbosity
                        if self.verbose: 
                            for stp in plan[i:]:
                                print('            '+step_to_str(stp)+color.fg_red(' '+u'\U0001F5D9'))
                            print(color.fg_red('      -- no valid progress  -- already unsolvable state by: %s' % step_to_str(step)))
                        # state is partially unsolvable
                        if self.unsolvable_states[state] is not None:
                            self.unsolvable_states[state].update(set(step))
                        # add also to temporary unsolvable_states
                        if unsolvable_states[state] is not None:
                            unsolvable_states[state].update(set(step))

                        # # check if this partial plan might lead to a loop in self.policy
                        # # if so, then ignore the current plan and add initial state into self.unsolvable_states
                        # loop = False
                        # while state in policy or state in self.policy:

                        #     loop = True

                        #     # remove the last state and step from policy
                        #     state, step = policy.popitem()

                        #     # add to temporary unsolvable_states
                        #     if unsolvable_states[state] is not None: 
                        #         unsolvable_states[state].update(set(step))

                        #     # verbosity
                        #     if self.verbose: print(color.fg_red2('      -- lead to an infinite loop by: %s %s' % (step_to_str(step) , u'\U0001F6C8')))

                        #     if not policy: break

                        #     # pop and insert again the last state and step from policy
                        #     state, step = policy.popitem()
                        #     policy[state] = step

                        #     if unsolvable_states[state] is not None:
                        #         unsolvable_states[state].update(set(step))

                        # if loop:  break

                        # check if this partial plan might lead to a loop in self.policy
                        # if so, then ignore the current plan and add initial state into unsolvable_states
                        if state in policy or state in self.policy:
                            # verbosity
                            if self.verbose: print(color.fg_red2('      -- lead to an infinite loop by: %s' % u'\U0001F6C8'))

                            # make state temporary partially unsolvable by the current step
                            if unsolvable_states[state] is not None:
                                if state in policy:
                                    unsolvable_states[state].update(set(policy[state]))
                                if state in self.policy:
                                    unsolvable_states[state].update(set(self.policy[state]))
                                unsolvable_states[state].update(set(step))
                            break

                        return policy

                    if self.verbose:
                        print('            '+step_to_str(step)+color.fg_yellow2(' '+u'\U0001F5F8'))

                    # add the current step into the current policy
                    policy[state] = step
                    state = new_state

                # inner for-loop finished with no break: the plan is valid 
                else:
                    return policy

                # inner for-loop was broken, then break outer for-loop too
                break

            # outer for-loop finished with no solution found for all domains
            else:
                # if policy is empty return failure 
                if not policy: return None

                # state is fully unsolvable
                unsolvable_states[state] = None

                # last state is partially unsolvable
                state, step = policy.popitem()
                if unsolvable_states[state] is not None:
                    unsolvable_states[state].update(set(step))

                # verbosity
                if self.verbose: 
                    if unsolvable_states[state] is not None:
                        print(color.fg_red('    -- unsolvable -- backtracking by excluding: %s' % step_to_str(unsolvable_states[state])))
                    else:
                        print(color.fg_red('    -- unsolvable -- backtracking'))


    ###################################################################
    #### NDP2 algorithm
    ###################################################################

    def find_safe_policy_ndp2(self):
        '''main loop of the planner -- returns a policy if any exists'''
        # if the initial state already contains the goal (then the plan is empty)
        if self.problem.initial_state.is_true(self.problem.goals):
            self.policy[self.problem.initial_state] = None
            # verbosity
            if self.verbose: print(color.fg_yellow('[Initial state already contains the goal!]'))
            return

        while True:

            # verbosity: info about time and replanning numbers
            if self.verbose:
                print(color.fg_yellow('\n(%s:%s replanning) (%s unsolvable states) [%.3f s]' %\
                    (self.alloutcome_planning_call, self.singleoutcome_planning_call, \
                        len(self.unsolvable_states), time.time() - self.planning_time)))

            # find a non-goal terminal state in the current policy
            state = self._find_open_terminal_state()

            # if no non-goal terminal state exists then return the current policy and finish the for-loop
            if state is None: 
                # first refine the policy
                self.refine_policy()
                return 

            # find a plan at the current state
            policy = self.find_safe_plan_ndp2(state)

            # if a policy is found then merge it into the resulting self.policy
            if policy is not None:
                self.policy = self.merge_policy(self.policy, policy)

                ## in case of 'ff-x': derived predicates are not yet supported, so terminates the 
                ## loop as soon as a solution is found (because the goal might not be achievable)
                ## THIS IS NOT SOUND AND MIGHT LEAD TO INACCURATE GOALS
                if len(self.domain.derived_predicates) > 0:
                    # simulate the problem goals
                    for state, step in self.policy.items():
                        for new_state in self.apply_step(init=state, step=step):
                            self.problem.goals = tuple(new_state.predicates)
                    return

            # if no plan found at the initial state then no policy exists and finish the loop
            elif state == self.problem.initial_state: 
                # verbosity
                if self.verbose: print(color.fg_red('\n-- no plan at the initial state %s' % u'\U0001F593'))
                # first refine the policy
                self.refine_policy()
                return 

            # otherwise; the current open terminal state is unsolvable 
            # add this state and all states leading to this state into unsolvable_states 
            # and remove those states from self.policy
            else:
                # fully unsolvable state
                self.unsolvable_states[state] = None

                # put in the self.unsolvable_states all states leading to 'state' and remove their path from self.policy
                for (s, step) in [(s, step) for (s, step) in self.policy.items() \
                        if state in self.apply_step(init=s, step=step)]:
                    # remove all states from 's' in self.policy
                    self.remove_path(s)
                    # # state is partially unsolvable
                    # if self.unsolvable_states[s] is not None:
                    #     self.unsolvable_states[s].update(set(step))
                    # verbosity
                    if self.verbose: 
                        print(color.fg_red2('  -- unsolvable by: %s %s' % (step_to_str(step), u'\U0001F593')))


    def find_safe_plan_ndp2(self, state):
        '''
        extend the policy and make a plan from the given state 
        @state : a given state that a plan is made on it
        '''
        # in some small problems, the state may become empty by the step application
        if len(state) == 0:
            if self.verbose: print(color.fg_red('  -- empty state %s' % u'\U0001F593'))
            return None

        policy = OrderedDict()
        unsolvable_states = self.unsolvable_states.copy()

        while True:

            # check if the given state is already unsolvable
            if state in unsolvable_states:
                # then return failure (None) if it is fully unsolvable
                if unsolvable_states[state] is None:
                    if self.verbose: print(color.fg_red('    -- already unsolvable %s' % u'\U0001F593'))
                    return None
                # verbosity
                if self.verbose: print(color.fg_red('    -- partially unsolvable  -- excluding: %s' % step_to_str(unsolvable_states[state])))

            ## return current plan (policy) if state is a goal state
            #if state.is_true(self.problem.goals):
                #return policy

            # increase the number of planning call
            self.alloutcome_planning_call += 1

            # verbosity: when verbosity is off: remove recorded files!
            if not self.verbose:
                if self.alloutcome_planning_call > 100 and self.alloutcome_planning_call % 100 == 0:
                    try:
                        os.system('rm -fr ' + self.working_dir + '*.pddl')
                    except OSError as e:
                        print("Error: %s : %s" % (dir_path, e.strerror))

            # modify state such that plan does not start with an action in self.unsolvable_states[state]
            # and create a pddl problem given retrieved 'state' as its initial state 
            if state in unsolvable_states:
                problem_pddl = pddl.pddl(self.problem, \
                    state=state.constrain_state(unsolvable_states[state], self.map_actions, self.prob_actions), \
                    path=self.working_dir)
            else:
                problem_pddl = pddl.pddl(self.problem, state=state, path=self.working_dir)

            for domain_pddl, domain_obj in self.domains.items():
                # modify domain such that plan does not start with an action in self.unsolvable_states[state]
                if state in unsolvable_states:
                    cons_domain_obj = domain_obj.constrain_domain(unsolvable_states[state], self.map_actions, self.prob_actions)
                else:
                    cons_domain_obj = domain_obj
                # create a pddl file of the domain object
                cons_domain_pddl = pddl.pddl(cons_domain_obj, path=self.working_dir)

                if self.verbose: 
                    print(color.fg_yellow2('    -- problem:') + problem_pddl)
                    print(color.fg_yellow2('    -- domain:') + cons_domain_pddl)

                # call the external classical planner
                # plan = call_planner(self.planners, cons_domain_pddl, problem_pddl, verbose=self.verbose)
                plan = external_planner.Plan(self.planners, cons_domain_pddl, problem_pddl, self.working_dir, verbose=self.verbose)

                # increase the number of planning call
                self.singleoutcome_planning_call += 1

                # verbosity: when verbosity is off !
                if not self.verbose:
                    if self.singleoutcome_planning_call > 0 and self.singleoutcome_planning_call % 500 == 0:
                        print(color.fg_yellow('(%s:%s replanning) (%s unsolvable states) [%.3f s]' %\
                            (self.alloutcome_planning_call, self.singleoutcome_planning_call, \
                                len(unsolvable_states), time.time() - self.planning_time)))

                # if no plan exists try the next domain
                if plan == None:
                    if self.verbose: print(color.fg_red('      -- no plan exists %s' % u'\U0001F593'))
                    continue

                # verbosity -- printout the resulting plan
                # if self.verbose == 1: print_classical_plan(plan)
                if self.verbose == 1: print(color.fg_yellow2('    -- plan:'))

                # make policy image of the plan and append it to the current policy 
                # if the plan has unsolvable states stop appending and continue planning 
                # from the last unsolvable state in the plan
                for i, step in enumerate(plan):
                    # make full grounded specification of actions and apply them in the state
                    new_state = self.apply_step(init=state, step=step, domain=domain_obj)

                    # check if the new_states are already in unsolvable_states
                    # or part of the current policy (to avoid cycles)
                    if new_state in policy or \
                       any([True for s in self.apply_step(init=state, step=step) \
                             if s in unsolvable_states and unsolvable_states[s] is None]) \
                       or (state in unsolvable_states and unsolvable_states[state] is not None and \
                           set(step).issubset(unsolvable_states[state])):
                        # verbosity
                        if self.verbose: 
                            for stp in plan[i:]:
                                print('            '+step_to_str(stp)+color.fg_red(' '+u'\U0001F5D9'))
                            print(color.fg_red('      -- no valid progress -- already unsolvable/looping state by: %s' % step_to_str(step)))
                        # state is partially unsolvable
                        unsolvable_states[state].update(set(step))
                        break
                    
                    # verbosity
                    if self.verbose:
                        print('            '+step_to_str(step)+color.fg_yellow2(' '+u'\U0001F5F8'))

                    # add the current step into the current policy
                    policy[state] = step
                    state = new_state

                # inner for-loop finished with no break: the plan is valid 
                else:
                    return policy

                # inner for-loop was broken, then break outer for-loop too
                break

            # outer for-loop finished with no solution found for all domains
            else:
                # if policy is empty return failure 
                if not policy: return None

                # state is fully unsolvable
                unsolvable_states[state] = None
                # this is tricky; might not be needed
                self.unsolvable_states[state] = None

                # last state is partially unsolvable
                state, step = policy.popitem()
                try: unsolvable_states[state].update(set(step))
                except: pass
                # this is tricky; might not be needed
                try: self.unsolvable_states[state].update(set(step))
                except: pass

                # verbosity
                if self.verbose: print(color.fg_red('    -- unsolvable -- backtracking by excluding: %s' % step_to_str(unsolvable_states[state])))


    ###################################################################

    def find_open_terminal_state(self):
        '''finds a non-goal terminal state in self.policy and returns if for expansion'''

        # policy is empty
        if not self.policy or not self.problem.initial_state in self.policy:
            if self.verbose: print(color.fg_yellow('\n-- expand the initial state'))
            # this is tricky; normally it should not be needed
            self.policy = OrderedDict()
            return self.problem.initial_state

        # find and return the first non-goal terminal state
        queue = [self.problem.initial_state]
        visited = set()

        while queue:
            state = queue.pop(0) # FIFO
            visited.add(state)

            if state in self.policy:
                for new_state in self.apply_step(init=state, step=self.policy[state]):
                    if not new_state in visited:
                        if new_state in self.policy:
                            queue.append(new_state)
                        elif not new_state.is_true(self.problem.goals):
                            if self.verbose: print(color.fg_yellow('\n-- expand an open terminal state produced by: ')+\
                                                ' '.join([str('('+' '.join(a)+')') for a in self.policy[state]]))
                            return new_state

        # all terminal states are goal states
        if self.verbose: print(color.fg_yellow('\n-- no more open terminal states %s' % u'\U0001F592'))
        return None


    def _find_open_terminal_state(self):
        '''finds a non-goal terminal state in self.policy and returns if for expansion'''
        # policy is empty or initial state is not in the policy
        if not self.policy or not self.problem.initial_state in self.policy:
            if self.verbose: print(color.fg_yellow('\n-- expand the initial state'))
            # this is tricky; normally it should not be needed
            self.policy = OrderedDict()
            return self.problem.initial_state

        for state, step in self.policy.items():
            for new_state in self.apply_step(init=state, step=step):
                if not new_state in self.policy and not new_state.is_true(self.problem.goals):
                    if self.verbose: print(color.fg_yellow('\n-- expand an open terminal state produced by: ')+step_to_str(step))
                    return new_state

        # all terminal states are hopefully goal states
        if self.verbose: print(color.fg_yellow('\n-- no more open terminal states %s' % u'\U0001F592'))
        return None


    def _find_open_terminal_state2(self):
        '''finds a non-goal terminal state in self.policy and returns if for expansion'''
        # policy is empty or initial state is not in the policy
        if not self.policy:
            if self.verbose: print(color.fg_yellow('\n-- expand the initial state'))
            return self.problem.initial_state

        for state, step in self.policy.items():
            for new_state in self.apply_step(init=state, step=step):
                if not new_state in self.policy and not new_state.is_true(self.problem.goals):
                    if self.verbose: print(color.fg_yellow('\n-- expand an open terminal state produced by: ')+step_to_str(step))
                    return new_state

        # all terminal states are hopefully goal states
        if self.verbose: print(color.fg_yellow('\n-- no more open terminal states %s' % u'\U0001F592'))
        return None


    def find_open_terminal_state2(self):
        '''finds a non-goal terminal state in self.policy and returns if for expansion'''
        for state, step in self.policy.items():
            if step is not None:
                for new_state in self.apply_step(init=state, step=step):
                    if not new_state in self.policy and not new_state.is_true(self.problem.goals):
                        if self.verbose: print(color.fg_yellow('\n-- expand an open terminal state produced by: ')+step_to_str(step))
                        return new_state
            elif not state.is_true(self.problem.goals):
                if self.verbose: print(color.fg_yellow('\n-- expand an open terminal state'))
                return state
        # # all terminal states are goal states
        # if self.policy: 
        #     for state, step in self.policy.items():
        #         if state.is_true(self.problem.goals):
        #             break
        #     else:
        #         if self.verbose: print(color.fg_red('\n-- there are no goal states %s' % u'\U0001F593'))
        #         # return self.problem.initial_state
        #         exit()
        # all terminal states are goal states
        if self.policy: 
            if self.verbose: print(color.fg_yellow('\n-- no more open terminal states %s' % u'\U0001F592'))
            return None
        # policy is empty
        if self.verbose: print(color.fg_yellow('\n-- expand the initial state'))
        return self.problem.initial_state


    def merge_policy(self, policy1, policy2, preserve=False):
        '''
        update policy1 by policy2 but skips already existed items
        @policy1 : the main given and the output policy
        @policy2 : the given policy to be merged into @policy1
        @preserve : if True, preserve old values in policy1 (i.e., 
                        do not update the old values if any exists)
        '''
        for state, step in policy2.items():
            if state not in policy1:
                policy1[state] = step
            elif not preserve:
                # for s in self.apply_step(state, policy1[state]):
                #     self.remove_path(s)
                policy1[state] = step
        return policy1


    def remove_path(self, state):
        '''
        remove all path starting from @state in self.policy
        '''
        if state in self.policy:
            step = self.policy[state]
            if self.verbose: print(color.fg_yellow('    -- removed from policy: ') + step_to_str(step))
            del self.policy[state]

            for s in self.apply_step(init=state, step=step):
                if s in self.policy:
                    self.remove_path(s)


    # def remove_path(self, state):
    #     '''
    #     remove all path starting from @state in self.policy
    #     '''
    #     if state in self.policy:
    #         step = self.policy[state]
    #         if self.verbose and step is not None: 
    #             print(color.fg_yellow('    -- removed from policy: ') + step_to_str(step))
    #         del self.policy[state]
    #         if step == None: return

    #         for s in self.apply_step(init=state, step=step):
    #             ## exclude states that in some domains a non-deterministic action 
    #             ## leads to the previous state (the state before action application)
    #             # if s in self.policy and self.policy[s] is not None and \
    #             #     not state in self.apply_step(init=s, step=self.policy[s]):
    #             #     self.remove_path(s)
    #             # elif s in self.policy and self.policy[s] is None:
    #             if s in self.policy:
    #                 self.remove_path(s)


    def achieve_goal(self, state):
        '''
        test if the given @state can achieve a goal state
        '''
        if state.is_true(self.problem.goals):
            return True

        if state in self.policy:
            step = self.policy[state]
            if step == None: return False

            for s in self.apply_step(init=state, step=step):
                return self.achieve_goal(s)

        return False


    def remove_path2(self, state, goal):
        '''
        remove all path starting from @state in self.policy
        '''
        if state == goal:
            return
        if state in self.policy:
            step = self.policy[state]
            if self.verbose and step is not None: 
                print(color.fg_yellow('    -- removed from policy: ') + step_to_str(step))
            del self.policy[state]
            if step == None: return

            # add to unsolvable_states
            if state in self.unsolvable_states and self.unsolvable_states[state] is not None: 
                # partially unsolvable state
                self.unsolvable_states[state].update(set(step))

            for s in self.apply_step(init=state, step=step):
                ## exclude states that in some domains a non-deterministic action 
                ## leads to the previous state (the state before action application)
                if s in self.policy:
                    self.remove_path2(s, goal)


    def apply_step(self, init, step, domain=None, det_effect_inc=False):
        '''
        return a state resulting from the application of actions in the step
        @init : the initial state that the step has to apply on it
        @step : a sequence of (concurrent) fully grounded actions
        @domain : if domain is given one state is generated from the application 
                      of the step on init, if the domain is not given, all domains are 
                      used and a list of states are genearted from the application of 
                      the step on init
        '''

        if step is None:
            if self.verbose: print(color.bg_voilet('## step is None!!'))
            if domain is not None: return init
            return OrderedDict([(init, [])])

        # if the domain is given, only action signatures in step are grounded
        # based on the given domain specification
        if domain is not None:
            for action in step:
                init = init.apply(domain.exclusive_ground(action))
            return init

        # else:
        # if the domain is not given, all domains are used to make ground 
        # probabilistic action signatures (note, only one domain is sufficient 
        # to make ground deterministic action signatures)
        grounded_steps = list()
        # if there is a probabilistic action in step, make ground all possible combination of actions on all domains
        if any([action for action in step if action[0] in self.prob_actions]):
            # for domain, domain_obj in self.domains.items():
            #     grounded_steps.append([domain_obj.inclusive_ground(action) for action in step])
            grounded_actions = list()
            for action in step:
                # grounded_action = set()
                # for domain, domain_obj in self.domains.items():
                #     grounded_action |= set(domain_obj.all_inclusive_ground(action, self.map_actions))
                # grounded_actions.append(tuple(grounded_action))
                ## the above loop is not needed anymore; the last domain is the all-outcome compilation 
                ## and is sufficient to ground all determinized actions of the non-deterministic action
                ## pick the last domain object
                domain, domain_obj = next(reversed(self.domains.items()))
                grounded_actions.append(tuple(domain_obj.all_inclusive_ground(action, self.map_actions)))
            ## generate all possible combination of actions
            grounded_steps = list(product(*grounded_actions))
        # otherwise, making ground on the first domain is sufficient
        else:
            # pick up the first domain object
            for domain, domain_obj in self.domains.items():
                grounded_steps.append([domain_obj.inclusive_ground(action, self.map_actions) for action in step])
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
                if state.is_true(grounded_action.preconditions.pos_preconditions,\
                                 grounded_action.preconditions.neg_preconditions):
                    state = state.apply(grounded_action)
            states[state] = (add_effects, del_effects)

        return states


    def refine_policy(self):
        '''refines the self.policy and removes all unreachable states'''
        # policy is empty
        if not self.policy or not self.problem.initial_state in self.policy:
            self.policy = OrderedDict()
            return

        policy = OrderedDict()
        queue = [self.problem.initial_state]

        while queue:
            state = queue.pop(0) # FIFO
            policy[state] = self.policy[state]

            if state in self.policy:
                for new_state in self.apply_step(init=state, step=self.policy[state]):
                    if not new_state in policy and not new_state.is_true(self.problem.goals):
                        queue.append(new_state)

        # copy the refined policy into self.policy
        self.policy = policy
        return


    def plan(self, tree=False, det_effect_inc=True):
        '''
        return an ordered dict as the final plan:
        the keys represent the steps of actions in the plan,
        the values are tuples of actions to be executed and outcome conditions 
        every sequence of actions in each step is followed by pairs of 
        conditions and a level to jump. the conditions are the outcome of 
        the actions that should be achieved after their execution.
        @tree : if True, plan is tree-like. it will include goal states 
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
        '''
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
                        # if self.verbose: print(color.fg_green('[Goal is achieved]'))
                        plan[i] = 'GOAL'
                    else:
                        if self.verbose: print(color.bg_red('[Goal is not achieved!]'))
                        plan[i] = None
                else:
                    states = self.apply_step(init=state, step=step, det_effect_inc=det_effect_inc)

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

                    plan[i] = (tuple([self.domain.inclusive_ground(action, self.map_actions) for action in step]), tuple(next_steps))

        return plan


    def print_plan(self, plan=None, del_effect_inc=False, det_effect_inc=False):
        '''
        print the plan in a more readable form
        '''
        if plan == None:
            plan = self.plan(det_effect_inc=det_effect_inc)

        print(color.bg_yellow('@ PLAN'))

        plan_str = str()
        for level, step in plan.items():
            if level == 'GOAL': continue
            plan_str+= '{:2} : '.format(level)
            if step == 'GOAL': 
                plan_str+= color.fg_beige('GOAL')
            elif step == None: 
                plan_str+= color.fg_voilet('None!')
            else:
                (actions, outcomes) = step
                plan_str+= '{{{}}}'.format(' '.join(map(str, actions)))
                for (conditions, jump) in outcomes:
                    ## represent jump in different color
                    jump_str = color.fg_voilet(str(jump))  # voile if there is a jump
                    if jump == 'GOAL': jump_str =color.fg_beige(str(jump))  # beige if it is a goal

                    # unfold conditions as add and delete lists
                    # if there is non-deterministic outcomes
                    if any([action.sig for action in actions if action.sig[0] in self.prob_actions]):
                    # if len(conditions) > 0: 
                        (add_list, del_list) = conditions
                        # if there is non-deterministic delete list in outcomes
                        if del_effect_inc and len(del_list) > 0:
                            plan_str+= color.fg_yellow(' -- {{{}}} \\ {{{}}} {}'.format( \
                                    ''.join(['({0})'.format(' '.join(map(str, c))) for c in add_list]), \
                                    ''.join(['({0})'.format(' '.join(map(str, c))) for c in del_list]), \
                                    jump_str))
                        # otherwise, exclude delete list in the representation of the plan
                        else:
                            plan_str+= color.fg_yellow(' -- {{{}}} {}'.format( \
                                    ''.join(['({0})'.format(' '.join(map(str, c))) for c in add_list]), \
                                    jump_str))
                    elif det_effect_inc:
                        (add_list, del_list) = conditions
                        if del_effect_inc and len(del_list) > 0:
                            plan_str+= color.fg_yellow(' -- {{{}}} \\ {{{}}} {}'.format( \
                                    ''.join(['({0})'.format(' '.join(map(str, c))) for c in add_list]), \
                                    ''.join(['({0})'.format(' '.join(map(str, c))) for c in del_list]), \
                                    jump_str))
                        else:
                            plan_str+= color.fg_yellow(' -- {{{}}} {}'.format( \
                                    ''.join(['({0})'.format(' '.join(map(str, c))) for c in add_list]), \
                                    jump_str))
                    else:
                        plan_str+= color.fg_yellow(' -- {{}} {}'.format(jump_str))
            plan_str+= '\n'
        print(plan_str)


    def get_paths(self, plan=None):
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
            plan = self.plan()

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


    def print_paths(self, plan=None, paths=None, del_effect_inc=False):
        '''
        print the paths of plan in a more readable form
        '''
        if paths == None:
            paths = self.get_paths(plan)

        if paths == list(): return

        print(color.bg_yellow('@ SUBPATHS'))

        p = 1
        for path in paths:
            print(color.fg_yellow('-- path{} ({})'.format(str(p), len(path))))
            p += 1
            plan_str = str()
            for (level, step) in path.items():
                plan_str+= '{:2} : '.format(level)
                if step == 'GOAL': 
                    plan_str+= color.fg_beige('(DONE)')
                elif step == None: 
                    plan_str+= color.fg_voilet('None!')
                else:
                    (actions, outcomes) = step
                    plan_str+= '{}'.format(' '.join(map(str, actions)))
                    (conditions, jump) = outcomes[0]
                    ## represent jump in different color
                    jump_str = color.fg_voilet(str(jump))  # voile if there is a jump
                    if jump == 'GOAL': jump_str =color.fg_beige(str(jump))  # beige if it is a goal

                    # unfold conditions as add and delete lists
                    # if there is non-deterministic outcomes
                    if any([action.sig for action in actions if action.sig[0] in self.prob_actions]):
                        (add_list, del_list) = conditions
                        # if there is non-deterministic delete list in outcomes
                        if del_effect_inc and len(del_list) > 0:
                            plan_str+= color.fg_yellow(' -- ({})({}) {}'.format( \
                                    ' '.join(['({0})'.format(' '.join(map(str, c))) for c in add_list]), \
                                    ' '.join(['({0})'.format(' '.join(map(str, c))) for c in del_list]), \
                                    jump_str))
                        # otherwise, exclude delete list in the representation of the plan
                        else:
                            plan_str+= color.fg_yellow(' -- ({}) {}'.format( \
                                    ' '.join(['({0})'.format(' '.join(map(str, c))) for c in add_list]), \
                                    jump_str))
                    else:
                        plan_str+= color.fg_yellow(' -- () {}'.format(jump_str))
                plan_str+= '\n'
            print(plan_str)


    def log_performance(self, plan):
        '''stores the planner performance in a file next to given problem file'''
        # create a stat file
        import json
        performance = {'planning_time':round(self.planning_time,3),\
                       'compilation_time':round(self.compilation_time,3),\
                       'planning_call_singlesoutcome':self.singleoutcome_planning_call,\
                       'planning_call_alloutcome':self.alloutcome_planning_call,\
                       'unsolvable_states':len(self.unsolvable_states),\
                       'solvable': 'GOAL' in plan.keys() or\
                                   'GOAL' in plan.values(),\
                       'policy_length':len(self.policy),\
                       'plan_length':len(plan)-1,
                       'deterministic_domains':len(self.domains)}
        if self.problem_file is not None:
            performance['arguments'] = ' '.join(sys.argv[3:])
            stat_file = '{}.stat'.format(os.path.splitext(self.problem_file)[0])
        else:
            performance['arguments'] = ' '.join(sys.argv[2:])
            stat_file = '{}.stat'.format(os.path.splitext(self.domain_file)[0])

        with open(stat_file, 'w') as outfile:
            json.dump(performance, outfile, indent=4)

        # append into a csv file for average performance of all problems in the domain directory
        # csv_file = '{}/{}.csv'.format(os.path.dirname(self.domain_file),self.domain.name)
        csv_file = '{}/results.csv'.format(os.path.dirname(self.domain_file))
        if os.path.exists(csv_file):
            with open(csv_file, 'a') as outfile:
                outfile.write('%s,%s,%.3f,%i,%i,%i,%i,%i,%i\n'%\
                    (os.path.basename(self.problem_file),self.problem.problem, \
                        self.planning_time, self.singleoutcome_planning_call, \
                        self.alloutcome_planning_call, len(self.unsolvable_states), \
                        'GOAL' in plan.keys() or 'GOAL' in plan.values(), len(self.policy), len(plan)-1 ))

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

def print_classical_plan(plan):
    '''print out given plan in a readable format'''
    if plan is None: return
    print(color.fg_yellow2('    -- plan:'))
    for step in plan:
        print('            '+' '.join([str('('+' '.join(action)+')') for action in step]))

def step_to_str(step):
    try:
        return ' '.join([str('('+' '.join(a)+')') for a in step])
    except:
        return 


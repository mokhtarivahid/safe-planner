#!/usr/bin/env python3

#################################
############# AJAY ##############
#################################
# import matlab.engine

import argparse
from collections import defaultdict, OrderedDict
from time import time

from color import fg_green, bg_green, fg_red, fg_yellow, bg_red, bg_yellow, fg_blue, fg_voilet, fg_beige, bg_voilet, bg_beige
from planner import Planner
from pddlparser import PDDLParser
# from pypddl import Domain, Problem, State, Action

## domains/hybrid/tabletop
# from domains.hybrid.tabletop import create_problem, objects_mat
# from domains.hybrid.robotic_arms import *
# from domains.hybrid.packaging import create_problem, objects_mat

import importlib

def parse():
    usage = 'python3 main.py <DOMAIN> [<PLANNER>] [-v | --verbose]'
    description = "hybrid planning interface for integrated symbolic and motion planning."
    parser = argparse.ArgumentParser(usage=usage, description=description)

    parser.add_argument('domain',  type=str, help='path to PDDL domain file')
    parser.add_argument('problem', type=str, help='path to PDDL problem file')
    parser.add_argument('planner', type=str, nargs='?', const=1, 
        help="external planner: ff, m, optic, vhpop, ... (default=ff)", default="ff")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", 
        action="store_true")

    return parser.parse_args()



###############################################################################
###############################################################################
if __name__ == '__main__':

    args = parse()

    ## from the given domain path import '__init__.py'
    # importlib.import_module('.'.join(map(str, args.domain.split('/')[:-1])))
    exec('from {} import *'.format('.'.join(map(str, args.domain.split('/')[:-1]))))

    print('--------------------------------------------------------------------------------')
    ## parse domain and create a domain object
    # domain = PDDLParser.parse(args.domain)

    ## call the matlab code and get the initial objects
    #################################
    ############# AJAY ##############
    #################################
    # objects_mat = eng.get_workspace_objects() or eng.workspace['obs_all']

    ## make an objects reference (given a symbolic name returns its index in objects_mat or vice versa)
    objects_ref = dict()

    for i in range(len(objects_mat)):
        object_name = str(objects_mat[i]['object_type'])+str(int(objects_mat[i]['index']))
        objects_ref[object_name] = i
        objects_ref[i] = object_name

    ## create an initial problem object by:
    ## 1) make a dictionary of objects (keys as types and values as objects)
    objects = defaultdict(list)

    for obj in objects_mat:
        object_name = str(obj['object_type'])+str(int(obj['index']))
        objects[obj['object_type']].append(object_name)

    # print(bg_yellow('@ objects_ref\n'), objects_ref)
    # print(bg_yellow('@ objects\n'), objects)

    ## 2) create a problem object given the objects
    # (problem_name, domain_name, objects, init, goal) = create_problem(objects)
    # problem = Problem(problem_name, domain_name, objects, init, goal)
    problem = PDDLParser.parse(args.problem)

    ## keep track of the current state and the current goal to achieve
    ## in any geometric limitation, the goal is updated to recover from 
    ## the failure situation (we do not plan again to the original goal)
    state = problem.initial_state
    goals = problem.goals

    ## test if the goal is already achieved (may not be necessary!)
    if state.is_true(*(problem.goals, problem.num_goals)):
        print('\nThe goal is already achieved')
        exit()

    # ## create a pddl problem file
    # problem_pddl = problem.pddl()

    # ## print out path to the problem pddl file
    # if args.verbose: print(fg_yellow('@ problem:'), problem_pddl)

    ## store the planning time and number of planning calls
    planning_time = time()
    planning_call = 0

    # ## call planner to make an initial policy given the domain, problem and planner
    # policy = Planner(args.domain, problem_pddl, args.planner, verbose=False)

    # ## print out the policy
    # if args.verbose: policy.print_plan()

    ## the refined final solution
    refined_plan = OrderedDict()

    ## current level of the plan
    level = 0

    ## loop until goal is achieved
    while not state.is_true(*(problem.goals, problem.num_goals)):
        ## create a pddl problem given the current state
        problem_pddl = problem.pddl(state, goals)

        ## print out some info
        if args.verbose: print(fg_yellow('@ problem:'), problem_pddl)

        ## call planner to make a plan given the domain, problem and planner
        policy = Planner(args.domain, problem_pddl, args.planner, args.verbose)
        # policy = Planner(args.domain, problem_pddl, args.planner)

        ## accumulate the planning calls
        planning_call += 1

        ## translate the policy into a cyclic contingency plan (tree)
        plan = policy.plan()

        ## print out the policy
        # if args.verbose: 
        policy.print_plan(plan)

        ## simulate and execute the plan
        while True:
            step = plan[level]

            if step == 'goal':
                # goal state is achieved
                print(bg_green('Goal achieved!'))
                break                

            ## print out the policy
            print(fg_green('@ step '+str(level)))

            if step == None:
                # normally shouldn't happen; otherwise, something is wrong (report it if happened)
                # anyway, it makes the plan a weak solution
                print(bg_voilet('None!'))
                print(bg_beige('plan gets an unsafe situation!'))
                print(bg_beige('normally should not happen; report it if please!'))
                print(bg_beige('anyhow the current plan is a weak solution!'))
                break
            else:
                # unfold step into a tuple of actoins and outcomes
                (actions, outcomes) = step

                for action in actions:
                    # print(fg_yellow('action -- '),action.__str__(True))
                    # exit()
                    
                    ## break the action into its name and args
                    action_name = action.sig[0]
                    action_args = action.sig[1:]

                    ## call matlab code to execute the action
                    ## check if the object is reachable by the robot
                    #################################
                    ############# AJAY ##############
                    #################################
                    # out_mat = eng.is_reachable_mat(action_name, action_args)
                    out_mat = True

                    ## if the action can be successfully executed then update the current state 
                    #################################
                    ############# AJAY ##############
                    #################################
                    # if out_mat['success'] == True:
                    if out_mat == True:
                        ## store the current action into the refined_plan
                        refined_plan.setdefault(level, []).append(action)

                        ## if the action is probabilistic check the output
                        ## !! it is not going to be implemented yet 
                        ## for now we always assume the first probabilistic effect is 
                        ## the intended one, so if the action is feasible it means the 
                        ## first probabilistic effects are applied; otherwise the second 
                        ## probabilistic effects are applied

                        # if action.name in policy.prob_actions:
                        #     print(bg_beige(action.__str__(body = True)))
                        #     print(outcomes)

                        ## apply the action to the current state
                        state = state.apply(action, prob_eff=0)

                        ## print out some info
                        # if args.verbose: 
                        print(fg_yellow(' + ') + action.__str__(body=False))


                    ## if there is some failure (infeasible)
                    else:
                        ## check the reachability of an arm to a grasp pose of an object
                        ## an exampel of grounded action: '(grasp left-arm obj1 obj1_gpt table1)'
                        ## it check the reachability of 'left-arm' to 'obj1_gpt'
                        ## if arm cannot reach the grasp pose (without any obstacle) then 
                        ## remove ('reachable', 'left-arm', 'obj1_gpt') from the current state
                        #################################
                        ############# AJAY ##############
                        #################################
                        # if action_args[0] cannot reach action_args[2]:
                        # out_mat['robot'][1]
                        # if out_mat['no_block']:
                        if False:

                            ## convert back the predicates frozenset to a list and update the state
                            ## e.g., remove ('reachable', 'left-arm', 'obj1_gpt')
                            state_predicates = list(state.predicates)
                            state_predicates.remove(('reachable', action_args[0], action_args[2]))
                            state.predicates = frozenset(state_predicates)

                            ## print out some info
                            # if args.verbose: 
                            print(fg_red(' - ') + action)
                            print(fg_red('@ arm', action_args[0], 'cannot reach', action_args[2]))

                        ## if there is an object blocking the target object
                        else:

                            ## return the obstructing objects
                            ## CURRENTLY WE ASSUME ONLY ONE OBJECT BLOCKS THE TARGET OBJECT!
                            #################################
                            ############# AJAY ##############
                            #################################
                            obstructing_object = out_mat['obs_blocking']

                            ## convert back the predicates frozenset to a list and update the state
                            ## e.g., remove ('unobstructed', 'obj1_gpl') and add ('obstructed', 'obj1_gpl', 'obj2')
                            state_predicates = list(state.predicates)
                            state_predicates.remove(('unobstructed', action_args[2]))
                            state_predicates.append(('obstructed', action_args[2], objects_ref[obstructing_object]))
                            state.predicates = frozenset(state_predicates)

                            ## print out some info
                            # if args.verbose: 
                            print(fg_red(' - ') + action)
                            print(fg_red('@', action_args[2], 'is obstructed by', objects_ref[obstructing_object]))

                        ## in either case break the for loop and make a replanning at the current updated state
                        ## note: the following three lines make sure to break from both (action and step) for-loops
                        break
                else:
                    ## continue if the action is successfully executed (the inner for-loop wasn't broken)
                    level += 1
                    continue
                ## inner loop was broken, break the outer too (either reachability or obstruction failure happened)
                break

    planning_time = time() - planning_time

    print('--------------------------------------------------------------------------------')
    print('Number of replannings: %s' % planning_call)
    print('Planning time: %.3f s' % planning_time)
    print('--------------------------------------------------------------------------------')

    # for level, step in refined_plan.items():
    #     for action in step:
    #         print(level, action.__str__(body=True))

    # print('--------------------------------------------------------------------------------')

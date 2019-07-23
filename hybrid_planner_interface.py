
import argparse

from collections import defaultdict, OrderedDict

from color import fg_green, fg_red, fg_yellow, fg_blue, fg_voilet, fg_beige, bg_voilet, bg_beige
from planner import Planner

from pddlparser import PDDLParser
from pypddl import Domain, Problem, State, Action
from external_planner import call_planner
from time import time



def parse():
    usage = 'python3 main.py <DOMAIN> [<PLANNER>] [-v | --verbose]'
    description = "hybrid planning interface for symbolic and motion planners."
    parser = argparse.ArgumentParser(usage=usage, description=description)

    parser.add_argument('domain',  type=str, help='path to PDDL domain file')
    # parser.add_argument('problem', type=str, help='path to PDDL problem file')
    parser.add_argument("planner", type=str, nargs='?', const=1, 
        help="external planner: ff, m, optic, vhpop, ... (default=ff)", default="ff")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", 
        action="store_true")

    return parser.parse_args()



objects_mat = [
   {'color': 'orange',
    'cuboid': 'matlab.double([[0.25],[0.5],[-0.25],[1.0],[1.0],[0.25]])',
    'object_type': 'robot',
    'type': 'cuboid',
    'index': 1.0},
   {'color': 'orange',
    'cuboid': 'matlab.double([[0.25],[0.5],[-0.25],[1.0],[1.0],[0.25]])',
    'object_type': 'robot',
    'type': 'cuboid',
    'index': 2.0},
   {'color': 'green',
    'cuboid': 'matlab.double([[0.25],[0.5],[-0.25],[1.0],[1.0],[0.25]])',
    'object_type': 'table',
    'type': 'cuboid',
    'index': 1.0},
   {'color': 'yellow',
    'cuboid': 'matlab.double([[0.25],[0.5],[0.05],[0.15],[0.25],[0.05]])',
    'object_type': 'crate',
    'type': 'cuboid',
    'index': 1.0},
   {'index': 1.0,
    'color': 'red',
    'cuboid': 'matlab.double([[0.2],[0.7],[0.35],[0.04],[0.04],[0.25]])',
    'object_type': 'object',
    'type': 'cuboid'},
   {'index': 2.0,
    'color': 'red',
    'cuboid': 'matlab.double([[-0.15],[0.35],[0.25],[0.04],[0.04],[0.25]])',
    'object_type': 'object',
    'type': 'cuboid'},
   {'index': 3.0,
    'color': 'red',
    'cuboid': 'matlab.double([[-0.15],[0.45],[0.05],[0.04],[0.04],[0.15]])',
    'object_type': 'object',
    'type': 'cuboid'},
   {'index': 4.0,
    'color': 'red',
    'cuboid': 'matlab.double([[-0.15],[0.55],[0.25],[0.04],[0.04],[0.25]])',
    'object_type': 'object',
    'type': 'cuboid'},
   {'index': 5.0,
    'color': 'red',
    'cuboid': 'matlab.double([[-0.15],[0.65],[0.25],[0.04],[0.04],[0.25]])',
    'object_type': 'object',
    'type': 'cuboid'},
   {'index': 6.0,
    'color': 'red',
    'cuboid': 'matlab.double([[0.65],[0.25],[0.25],[0.04],[0.04],[0.25]])',
    'object_type': 'object',
    'type': 'cuboid'},
   {'index': 7.0,
    'color': 'red',
    'cuboid': 'matlab.double([[0.65],[0.35],[0.25],[0.04],[0.04],[0.25]])',
    'object_type': 'object',
    'type': 'cuboid'},
   {'index': 8.0,
    'color': 'red',
    'cuboid': 'matlab.double([[0.65],[0.45],[0.25],[0.04],[0.04],[0.25]])',
    'object_type': 'object',
    'type': 'cuboid'},
   {'index': 9.0,
    'color': 'red',
    'cuboid': 'matlab.double([[0.65],[0.55],[0.25],[0.04],[0.04],[0.25]])',
    'object_type': 'object',
    'type': 'cuboid'},
   {'index': 10.0,
    'color': 'red',
    'cuboid': 'matlab.double([[0.65],[0.65],[0.25],[0.04],[0.04],[0.25]])',
    'object_type': 'object',
    'type': 'cuboid'} ]


###############################################################################
## create a problem object for 'robotic-arms' domain given a dictionary of objects
###############################################################################
def create_problem(objects):

    ## create the initial state
    predicates = list()

    # '(arm ?robot)'
    for r in objects['robot']:
        predicates.append(tuple(['arm',r]))

    # '(table ?table)'
    for t in objects['table']:
        predicates.append(tuple(['table',t]))

    # '(crate ?crate)'
    for c in objects['crate']:
        predicates.append(tuple(['crate',c]))

    # '(clear ?object)'
    for b in objects['object']:
        predicates.append(tuple(['clear',b]))

    # '(on ?object ?table)'
    for t in objects['table']:
        for b in objects['object']:
            predicates.append(tuple(['on',b,t]))

    # '(arm_canreach ?arm ?object)'
    for r in objects['robot']:
        for b in objects['object']:
            predicates.append(tuple(['arm_canreach',r,b]))

    # '(arm_free ?robot)'
    for r in objects['robot']:
        predicates.append(tuple(['arm_free',r]))


    ## create the goal
    goal = list()

    # '(in ?object ?crate)'
    for c in objects['crate']:
        for b in objects['object']:
            goal.append(tuple(['in',b,c]))

    ## create a problem object
    problem = Problem(problem='prob0', \
                      domain='robotic-arms', \
                      objects=dict(objects), \
                      init=predicates, \
                      goal=goal)

    return problem


###############################################################################
###############################################################################
if __name__ == '__main__':

    args = parse()

    ## parse domain and create a domain object
    domain = PDDLParser.parse(args.domain)

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

    ## 2) create the object given the objects
    problem = create_problem(objects)

    ## keep track of the current state
    state = problem.initial_state

    ## store the planning time and number of planning calls
    planning_time = time()
    planning_call = 0

    ## loop until goal is achieved
    while not state.is_true(*(problem.goals, problem.num_goals)):

        ## create a pddl problem given the current state
        problem_pddl = problem.pddl(state)

        ## print out some info
        if args.verbose: print(problem_pddl)

        ## call planner to make a plan given the domain, problem and planner
        plan = call_planner(args.domain, problem_pddl, args.planner, args.verbose)

        ## print out some info
        if args.verbose: 
            print(fg_yellow('@ plan'))
            for step in plan: print(step) 
            print()

        ## accumulate the planning calls
        planning_call += 1

        ## simulate and execute the plan
        for step in plan:
            for action in step:

                ## break the action into its name and args
                action_name = action[0]
                action_args = action[1:]

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
                if out_mat == True:
                    ## make a ground action and apply it to the current state
                    grounded_action = domain.ground(action)
                    state = state.apply(grounded_action)

                    ## print out some info
                    # if args.verbose: 
                    print(fg_yellow('+'), action)


                ## if there is some failure
                else:

                    ## if arm cannot reach the object (without any obstacle)
                    ## then remove ('arm_canreach', 'robot', 'object') from the current state
                    #################################
                    ############# AJAY ##############
                    #################################
                    # if action_args[0] cannot reach action_args[1]:
                    # out_mat['robot'][1]
                    # Out[19]: matlab.double([1.0])
                    if False:

                        ## convert back the predicates frozenset to a list and update the state
                        ## i.e., remove ('arm_canreach', 'robot', 'object')
                        state_predicates = list(state.predicates)
                        state_predicates.remove(('arm_canreach', action_args[0], action_args[1]))
                        state.predicates = frozenset(state_predicates)

                        ## print out some info
                        # if args.verbose: 
                        print(fg_red('-'), action)
                        print('@ arm', action_args[0], 'cannot reach', action_args[1])

                    ## if there is an object blocking the target object
                    else:

                        ## return the obstructing objects
                        ## CURRENTLY WE ASSUME ONLY ONE OBJECT BLOCKS THE TARGET OBJECT!
                        #################################
                        ############# AJAY ##############
                        #################################
                        blocking_object = out_mat['obs_blocking']

                        ## convert back the predicates frozenset to a list and update the state
                        ## i.e., remove ('clear', 'object') and add ('blocked', 'object', 'blocking_object')
                        state_predicates = list(state.predicates)
                        state_predicates.remove(('clear', action_args[1]))
                        state_predicates.append(('blocked', action_args[1], objects_ref[blocking_object]))
                        state.predicates = frozenset(state_predicates)

                        ## print out some info
                        # if args.verbose: 
                        print(fg_red('-'), action)
                        print('@', action_args[1], 'is blocked by', objects_ref[blocking_object])

                    ## in either case break the for loop and make a replanning at the current updated state
                    break


    planning_time = time() - planning_time

    print('\nNumber of replannings: %s' % planning_call)
    print('Planning time: %.3f s' % planning_time)


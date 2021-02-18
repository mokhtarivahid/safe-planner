from time import time
from collections import defaultdict

objects_mat = [
    ## robot
   {'color': 'orange',
    'cuboid': 'matlab.double([[0.25],[0.5],[-0.25],[1.0],[1.0],[0.25]])',
    'object_type': 'arm',
    'type': 'cuboid',
    'index': 1.0},
   {'color': 'orange',
    'cuboid': 'matlab.double([[0.25],[0.5],[-0.25],[1.0],[1.0],[0.25]])',
    'object_type': 'arm',
    'type': 'cuboid',
    'index': 2.0},
    ## object
   {'index': 1.0,
    'color': 'blue',
    'cuboid': 'matlab.double([[0.2],[0.7],[0.35],[0.04],[0.04],[0.25]])',
    'object_type': 'graspable',
    'type': 'cuboid',
    'filled': True},
   {'index': 2.0,
    'color': 'red',
    'cuboid': 'matlab.double([[-0.15],[0.35],[0.25],[0.04],[0.04],[0.25]])',
    'object_type': 'graspable',
    'type': 'cuboid',
    'filled': False,
    'location': 'table'},
   {'index': 3.0,
    'color': 'red',
    'cuboid': 'matlab.double([[-0.15],[0.35],[0.25],[0.04],[0.04],[0.25]])',
    'object_type': 'graspable',
    'type': 'cuboid',
    'filled': True} ]


###############################################################################
## create a problem object for 'crate' domain given a dictionary of objects
###############################################################################
def create_problem(objects, objects_mat=None):

    ## domain name
    domain = "pullandpick"

    ## pick a name for the problem
    problem = "prob"+str(int(time()))

    ## create the initial state
    init = list()

    # '(free ?arm)'
    for r in objects['arm']:
        init.append(tuple(['free',r]))

    # '(reachable ?arm ?object)'
    for a in objects['arm']:
        for o in objects['graspable']:
            if a == 'arm2' and o == 'graspable1': continue
            init.append(tuple(['reachable',a,o]))

    # '(ontable ?object)'
    for o in objects['graspable']:
        init.append(tuple(['ontable',o]))

    # '(ungrasped ?object)'
    for o in objects['graspable']:
        init.append(tuple(['ungrasped',o]))

    # '(unobstructed ?object)'
    for o in objects['graspable']:
        init.append(tuple(['unobstructed',o]))

    # '(nearby ?arm ?object)'
    for a in objects['arm']:
        for o in objects['graspable']:
            init.append(tuple(['nearby',o,a]))

    ## create the goal
    goal = list()

    # '(lifted ?object)''
    goal.append(tuple(['lifted',objects['graspable'][0]]))

    return (problem, domain, dict(objects), init, goal)


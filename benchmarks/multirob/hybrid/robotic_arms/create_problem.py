from time import time

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

    ## domain name
    domain = "robotic-arms"

    ## pick a name for the problem
    problem = "prob"+str(int(time()))

    ## create the initial state
    init = list()

    # '(arm ?robot)'
    for r in objects['robot']:
        init.append(tuple(['arm',r]))

    # '(table ?table)'
    for t in objects['table']:
        init.append(tuple(['table',t]))

    # '(crate ?crate)'
    for c in objects['crate']:
        init.append(tuple(['crate',c]))

    # '(clear ?object)'
    for b in objects['object']:
        init.append(tuple(['clear',b]))

    # '(on ?object ?table)'
    for t in objects['table']:
        for b in objects['object']:
            init.append(tuple(['on',b,t]))

    # '(arm_canreach ?arm ?object)'
    for r in objects['robot']:
        for b in objects['object']:
            init.append(tuple(['arm_canreach',r,b]))

    # '(arm_free ?robot)'
    for r in objects['robot']:
        init.append(tuple(['arm_free',r]))


    ## create the goal
    goal = list()

    # '(in ?object ?crate)'
    for c in objects['crate']:
        for b in objects['object']:
            goal.append(tuple(['in',b,c]))

    ## return a problem object's components
    return (problem, domain, dict(objects), init, goal)

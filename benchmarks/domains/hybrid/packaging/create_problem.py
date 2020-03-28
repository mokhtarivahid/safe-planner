from time import time

objects_mat = [
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
   {'color': 'green',
    'cuboid': 'matlab.double([[0.25],[0.5],[-0.25],[1.0],[1.0],[0.25]])',
    'object_type': 'surface',
    'type': 'cuboid',
    'index': 1.0},
   {'color': 'green',
    'cuboid': 'matlab.double([[0.25],[0.5],[-0.25],[1.0],[1.0],[0.25]])',
    'object_type': 'surface',
    'type': 'cuboid',
    'index': 2.0},
   {'color': 'yellow',
    'cuboid': 'matlab.double([[0.25],[0.5],[0.05],[0.15],[0.25],[0.05]])',
    'object_type': 'space',
    'type': 'cuboid',
    'index': 1.0},
   {'color': 'yellow',
    'cuboid': 'matlab.double([[0.25],[0.5],[0.05],[0.15],[0.25],[0.05]])',
    'object_type': 'space',
    'type': 'cuboid',
    'index': 2.0},
   {'color': 'yellow',
    'cuboid': 'matlab.double([[0.25],[0.5],[0.05],[0.15],[0.25],[0.05]])',
    'object_type': 'container',
    'type': 'cuboid',
    'index': 1.0},
   {'color': 'yellow',
    'cuboid': 'matlab.double([[0.25],[0.5],[0.05],[0.15],[0.25],[0.05]])',
    'object_type': 'package',
    'type': 'cuboid',
    'index': 1.0},
   {'color': 'yellow',
    'cuboid': 'matlab.double([[0.25],[0.5],[0.05],[0.15],[0.25],[0.05]])',
    'object_type': 'camera',
    'type': 'cuboid',
    'index': 1.0},
   {'index': 1.0,
    'color': 'red',
    'cuboid': 'matlab.double([[0.2],[0.7],[0.35],[0.04],[0.04],[0.25]])',
    'object_type': 'graspable',
    'type': 'cuboid'},
   {'index': 2.0,
    'color': 'red',
    'cuboid': 'matlab.double([[-0.15],[0.35],[0.25],[0.04],[0.04],[0.25]])',
    'object_type': 'graspable',
    'type': 'cuboid'},
   {'index': 3.0,
    'color': 'red',
    'cuboid': 'matlab.double([[-0.15],[0.45],[0.05],[0.04],[0.04],[0.15]])',
    'object_type': 'graspable',
    'type': 'cuboid'},
   {'index': 4.0,
    'color': 'red',
    'cuboid': 'matlab.double([[-0.15],[0.55],[0.25],[0.04],[0.04],[0.25]])',
    'object_type': 'graspable',
    'type': 'cuboid'},
   {'index': 5.0,
    'color': 'red',
    'cuboid': 'matlab.double([[-0.15],[0.65],[0.25],[0.04],[0.04],[0.25]])',
    'object_type': 'graspable',
    'type': 'cuboid'},
   {'index': 6.0,
    'color': 'red',
    'cuboid': 'matlab.double([[0.65],[0.25],[0.25],[0.04],[0.04],[0.25]])',
    'object_type': 'graspable',
    'type': 'cuboid'},
   {'index': 7.0,
    'color': 'red',
    'cuboid': 'matlab.double([[0.65],[0.35],[0.25],[0.04],[0.04],[0.25]])',
    'object_type': 'graspable',
    'type': 'cuboid'},
   {'index': 8.0,
    'color': 'red',
    'cuboid': 'matlab.double([[0.65],[0.45],[0.25],[0.04],[0.04],[0.25]])',
    'object_type': 'graspable',
    'type': 'cuboid'},
   {'index': 9.0,
    'color': 'red',
    'cuboid': 'matlab.double([[0.65],[0.55],[0.25],[0.04],[0.04],[0.25]])',
    'object_type': 'graspable',
    'type': 'cuboid'},
   {'index': 10.0,
    'color': 'red',
    'cuboid': 'matlab.double([[0.65],[0.65],[0.25],[0.04],[0.04],[0.25]])',
    'object_type': 'graspable',
    'type': 'cuboid'} ]


###############################################################################
## create a problem object for 'crate' domain given a dictionary of objects
###############################################################################
def create_problem(objects):

    ## domain name
    domain = "packaging"

    ## pick a name for the problem
    problem = "prob"+str(int(time()))

    ## create the initial state
    init = list()

    # '(arm ?arm)'
    for r in objects['arm']:
        init.append(tuple(['arm',r]))

    # '(surface ?surface)'
    # update the objects by adding an underscore '_' at the beginning
    # objects['surface'] = ['_'+t for t in objects['surface']]
    for t in objects['surface']:
        init.append(tuple(['surface',t]))

    # '(space ?space)'
    for t in objects['space']:
        init.append(tuple(['space',t]))

    # '(container ?container)'
    for t in objects['container']:
        init.append(tuple(['container',t]))

    # '(package ?package)'
    for t in objects['package']:
        init.append(tuple(['package',t]))

    # '(camera ?camera)'
    for t in objects['camera']:
        init.append(tuple(['camera',t]))

    # '(graspable ?graspable)'
    for t in objects['graspable']:
        init.append(tuple(['graspable',t]))

    # '(arm_canreach ?arm ?object)'
    for r in objects['arm']:
        for b in objects['surface']:
            # an arm can only reach its surface (related by the same index)
            if objects['arm'].index(r) == objects['surface'].index(b):
                init.append(tuple(['arm_canreach',r,b]))
        for b in objects['space']:
            # an arm can only reach its space (related by the same index)
            if objects['arm'].index(r) == objects['space'].index(b):
                init.append(tuple(['arm_canreach',r,b]))
        for b in objects['container']:
            init.append(tuple(['arm_canreach',r,b]))
        for b in objects['package']:
            init.append(tuple(['arm_canreach',r,b]))
        for b in objects['camera']:
            init.append(tuple(['arm_canreach',r,b]))
        for b in objects['graspable']:
            init.append(tuple(['arm_canreach',r,b]))

    # '(arm_free ?arm)'
    for r in objects['arm']:
        init.append(tuple(['arm_free',r]))

    # '(arm_at ?arm ?space)'
    for r in objects['arm']:
        for b in objects['space']:
            # an arm can only be at one space (related by the same index)
            if objects['arm'].index(r) == objects['space'].index(b):
                init.append(tuple(['arm_at',r,b]))

    # '(object_in ?graspable ?container)'
    for r in objects['graspable']:
        for b in objects['container']:
            init.append(tuple(['object_in',r,b]))

    # '(location_free ?location)'
    for r in objects['surface']:
        init.append(tuple(['location_free',r]))
    for r in objects['container']:
        init.append(tuple(['location_free',r]))
    for r in objects['package']:
        init.append(tuple(['location_free',r]))
    for r in objects['camera']:
        init.append(tuple(['location_free',r]))
    for r in objects['graspable']:
        init.append(tuple(['location_free',r]))

    # '(unblocked ?graspable)'
    for r in objects['graspable']:
        init.append(tuple(['unblocked',r]))

    ## create the goal
    goal = list()

    # '(packed ?graspable ?package)'
    for c in objects['package']:
        for b in objects['graspable']:
            goal.append(tuple(['packed',b,c]))

    ## refine object types: dut to a parser limitation of types hierarchy
    ## change the type of all objects to 'location' except 'arm'
    ## then we have only objects of two types: 'location' and 'arm'
    for b in objects['surface']:
        objects['location'].append(b)
        objects.pop('surface', None)
    for b in objects['space']:
        objects['location'].append(b)
        objects.pop('space', None)
    for b in objects['container']:
        objects['location'].append(b)
        objects.pop('container', None)
    for b in objects['package']:
        objects['location'].append(b)
        objects.pop('package', None)
    for b in objects['camera']:
        objects['location'].append(b)
        objects.pop('camera', None)
    for b in objects['graspable']:
        objects['location'].append(b)
        objects.pop('graspable', None)

    return (problem, domain, dict(objects), init, goal)


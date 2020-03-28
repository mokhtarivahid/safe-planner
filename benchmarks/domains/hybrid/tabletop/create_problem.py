from time import time
from collections import defaultdict

objects_mat = [
    ## table
   {'color': 'green',
    'cuboid': 'matlab.double([[0.25],[0.5],[-0.25],[1.0],[1.0],[0.25]])',
    'object_type': 'table',
    'type': 'cuboid',
    'index': 1.0},
    ## tray
   {'color': 'blue',
    'cuboid': 'matlab.double([[0.25],[0.5],[-0.25],[1.0],[1.0],[0.25]])',
    'object_type': 'tray',
    'type': 'cuboid',
    'index': 1.0},
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
    'object_type': 'object',
    'type': 'cuboid',
    'filled': True},
   {'index': 2.0,
    'color': 'red',
    'cuboid': 'matlab.double([[-0.15],[0.35],[0.25],[0.04],[0.04],[0.25]])',
    'object_type': 'object',
    'type': 'cuboid',
    'filled': False,
    'location': 'table'},
   {'index': 3.0,
    'color': 'red',
    'cuboid': 'matlab.double([[-0.15],[0.35],[0.25],[0.04],[0.04],[0.25]])',
    'object_type': 'object',
    'type': 'cuboid',
    'filled': True},
    ## grasp pose
    ## object 1
   {'index': 1.0,
    'color': None,
    'cuboid': 'matlab.double([[-0.15],[0.45],[0.05],[0.04],[0.04],[0.15]])',
    'object_type': 'grasp_pose',
    'type': 'cuboid',
    'pose': 'top',
    'object_ref': 'object',
    'object_index': 1.0},
   {'index': 2.0,
    'color': None,
    'cuboid': 'matlab.double([[-0.15],[0.45],[0.05],[0.04],[0.04],[0.15]])',
    'object_type': 'grasp_pose',
    'type': 'cuboid',
    'pose': 'left',
    'object_ref': 'object',
    'object_index': 1.0},
   {'index': 3.0,
    'color': None,
    'cuboid': 'matlab.double([[-0.15],[0.45],[0.05],[0.04],[0.04],[0.15]])',
    'object_type': 'grasp_pose',
    'type': 'cuboid',
    'pose': 'right',
    'object_ref': 'object',
    'object_index': 1.0},
    ## object 2
   {'index': 4.0,
    'color': None,
    'cuboid': 'matlab.double([[-0.15],[0.45],[0.05],[0.04],[0.04],[0.15]])',
    'object_type': 'grasp_pose',
    'type': 'cuboid',
    'pose': 'top',
    'object_ref': 'object',
    'object_index': 2.0},
   {'index': 5.0,
    'color': None,
    'cuboid': 'matlab.double([[-0.15],[0.45],[0.05],[0.04],[0.04],[0.15]])',
    'object_type': 'grasp_pose',
    'type': 'cuboid',
    'pose': 'left',
    'object_ref': 'object',
    'object_index': 2.0},
   {'index': 6.0,
    'color': None,
    'cuboid': 'matlab.double([[-0.15],[0.45],[0.05],[0.04],[0.04],[0.15]])',
    'object_type': 'grasp_pose',
    'type': 'cuboid',
    'pose': 'right',
    'object_ref': 'object',
    'object_index': 2.0},
    ## object 3
   {'index': 7.0,
    'color': None,
    'cuboid': 'matlab.double([[-0.15],[0.45],[0.05],[0.04],[0.04],[0.15]])',
    'object_type': 'grasp_pose',
    'type': 'cuboid',
    'pose': 'top',
    'object_ref': 'object',
    'object_index': 3.0},
   {'index': 8.0,
    'color': None,
    'cuboid': 'matlab.double([[-0.15],[0.45],[0.05],[0.04],[0.04],[0.15]])',
    'object_type': 'grasp_pose',
    'type': 'cuboid',
    'pose': 'left',
    'object_ref': 'object',
    'object_index': 3.0},
   {'index': 9.0,
    'color': None,
    'cuboid': 'matlab.double([[-0.15],[0.45],[0.05],[0.04],[0.04],[0.15]])',
    'object_type': 'grasp_pose',
    'type': 'cuboid',
    'pose': 'right',
    'object_ref': 'object',
    'object_index': 3.0} ]


###############################################################################
## create a problem object for 'crate' domain given a dictionary of objects
###############################################################################
def create_problem(objects, objects_mat=None):

    filled_objects = defaultdict(list)
    for obj in objects_mat:
        if 'filled' in obj:
            object_name = str(obj['object_type'])+str(int(obj['index']))
            if obj['filled'] == True:
                filled_objects['filled'].append(object_name)
            else:
                filled_objects['empty'].append(object_name)

    ## domain name
    domain = "tabletop"

    ## pick a name for the problem
    problem = "prob"+str(int(time()))

    ## create the initial state
    init = list()

    # '(free ?arm)'
    for r in objects['arm']:
        init.append(tuple(['free',r]))

    # '(ontable ?object ?table)'
    for t in objects['table']:
        for o in objects['object']:
            init.append(tuple(['ontable',o,t]))

    # '(filled ?object)'
    # for o in objects['object']:
    #     init.append(tuple(['filled',o]))
    for o in filled_objects['filled']:
        init.append(tuple(['filled',o]))
    for o in filled_objects['empty']:
        init.append(tuple(['empty',o]))

    # '(graspable ?object ?grasp_pose)'
    for i in range(len(objects['object'])):
        for j in range(i*3,(i+1)*3):
            init.append(tuple(['graspable',objects['object'][i],objects['grasp_pose'][j]]))

    # '(reachable ?arm ?grasp_pose)'
    for a in objects['arm']:
        for g in objects['grasp_pose']:
            if 'left' in g and 'arm1' in a: continue
            elif 'right' in g and 'arm2' in a: continue
            else: init.append(tuple(['reachable',a,g]))

    # '(unobstructed ?grasp_pose)'
    for g in objects['grasp_pose']:
        init.append(tuple(['unobstructed',g]))

    ## create the goal
    goal = list()

    # '(ontray ?object ?tray)'
    # goal.append(tuple(['ontray','object1','tray1']))
    # goal.append(tuple(['filled','object1']))
    # goal.append(tuple(['filled','object2']))
    # goal.append(tuple(['filled','object3']))
    # for o in objects['object']:
    #     goal.append(tuple(['filled',o]))
    for o in filled_objects['filled']:
        goal.append(tuple(['filled',o]))
    for o in filled_objects['empty']:
        goal.append(tuple(['empty',o]))

    # '(co_lifted ?object)''
    goal.append(tuple(['co_lifted','object1']))

    return (problem, domain, dict(objects), init, goal)


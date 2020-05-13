#!/usr/bin/env python
import sys, random
import os, time

#*****************#
# Functions declarations
#*****************#
def get_objects(num_robots, num_servicemen, num_nuts, num_spanners, num_toolboxes):
    str_objects="\n"

    # -- robot
    str_objects=str_objects+"     arm1"
    for i in range(2, num_robots+1):
        str_objects=str_objects+" arm"+str(i)
    str_objects=str_objects+" - robot\n    "

    # -- serviceman
    for i in range(1,num_servicemen+1):
        str_objects=str_objects+" serviceman"+str(i)
    str_objects=str_objects+" - serviceman\n    "

    # -- nut
    for i in range(1,num_nuts+1):
        str_objects=str_objects+" nut"+str(i)
    str_objects=str_objects+" - nut\n    "

    # -- spanner
    for i in range(1, num_spanners+1):
        str_objects=str_objects+" spanner"+str(i)
    str_objects=str_objects+" - spanner\n    "

    # -- toolbox
    for i in range(1,num_toolboxes+1):
        str_objects=str_objects+" toolbox"+str(i)
    str_objects=str_objects+" - toolbox\n    "

    # -- serviceman site
    str_objects=str_objects+" table"
    for i in range(1,num_servicemen+1):
        str_objects=str_objects+" serviceman_site"+str(i)
    str_objects=str_objects+" - location\n"

    return(str_objects)
    


#*****************#
def get_init(num_robots, num_servicemen, num_nuts, num_spanners, num_toolboxes):
    str_init="\n"
    # -- robot
    for i in range(1, num_robots+1):
        str_init=str_init+"    (at arm"+str(i)+" table)\n"
    for i in range(1, num_robots+1):
        str_init=str_init+"    (free arm"+str(i)+")\n"

    # -- serviceman
    for i in range(1,num_servicemen+1):
        str_init=str_init+"    (at serviceman"+str(i)+" serviceman_site"+str(i)+")\n"

    # -- spanner
    for i in range(1,num_spanners+1):
        str_init=str_init+"    (at spanner"+str(i)+" toolbox"+ str(random.randint(1,num_toolboxes))+")\n"
    for i in range(1,num_spanners+1):
        str_init=str_init+"    (useable spanner"+str(i)+")\n"

    # -- nut
    for i in range(1,num_nuts+1):
        str_init=str_init+"    (loose nut"+str(i)+")\n" 
    for i in range(1,num_nuts+1):
        str_init=str_init+"    (at nut"+str(i)+" table)\n"
    for i in range(1,num_nuts+1):
        str_init=str_init+"    (size nut"+str(i)+" spanner"+ str(random.randint(1,num_spanners))+")\n"

    # -- location
    # -- toolbox
    for i in range(1,num_toolboxes+1):
        str_init=str_init+"    (link toolbox"+str(i)+" table)\n"
        str_init=str_init+"    (link table toolbox"+str(i)+")\n"

    for i in range(1,num_toolboxes):
        for j in range(i+1,num_toolboxes+1):
            str_init=str_init+"    (link toolbox"+str(i)+" toolbox"+str(j)+")\n"
            str_init=str_init+"    (link toolbox"+str(j)+" toolbox"+str(i)+")\n"

    # -- serviceman
    for i in range(1,num_servicemen+1):
        str_init=str_init+"    (link serviceman_site"+str(i)+" table)\n"
        str_init=str_init+"    (link table serviceman_site"+str(i)+")\n"

    return(str_init)

#*****************#
def get_goals(num_nuts, num_spanners):
    str_goal=""
    str_goal=str_goal+"\n  (and\n"

    for i in range(1,num_nuts+1):
        str_goal=str_goal+ "    (tightened nut"+str(i)+")\n"
                
    str_goal=str_goal+")"
    return(str_goal)

#*****************#
def gen_problem(num_robots, num_servicemen, num_nuts, num_spanners, num_toolboxes):

    random.seed()

    name="prob_%s_%s_%s_%s_%s" % (str(num_robots), str(num_servicemen), \
                str(num_nuts), str(num_spanners), str(num_toolboxes))

    pddl_str = ";; prob_robots_servicemen_nuts_spanners_toolboxes\n"
    pddl_str += "(define (problem "+name+")\n"
    pddl_str += "(:domain spanner)\n"
    pddl_str += "(:objects "+ get_objects(num_robots, num_servicemen, num_nuts, \
                                          num_spanners, num_toolboxes)+")\n"
    pddl_str += "(:init " + get_init(num_robots, num_servicemen, num_nuts, \
                                     num_spanners, num_toolboxes)+")\n"
    pddl_str += "(:goal"+ get_goals(num_nuts, num_spanners)+"))"

    return pddl_str

#*****************#
# MAIN
#*****************#
if __name__ == '__main__':

    # Reading the command line arguments
    try:
        num_robots = int(sys.argv[1])
        num_servicemen =  int(sys.argv[2])
        num_nuts =  int(sys.argv[3])
        num_spanners = int(sys.argv[4])
        num_toolboxes = int(sys.argv[5])
    except:
        print "Usage: "+sys.argv[0]+" <num_robots> <num_servicemen> <num_nuts> <num_spanners> <num_toolboxes>"
        print "  num_robots (min 1)"
        print "  num_servicemen (min 1)"
        print "  num_nuts (min 1)"
        print "  num_spanners (min 1 and <= num_nuts)"
        print "  num_toolboxes (min 1 and <= num_spanners)"

        sys.exit(1)

    pddl_str = gen_problem(num_robots, num_servicemen, num_nuts, num_spanners, num_toolboxes)

    print(pddl_str)

    name="prob_%s_%s_%s_%s_%s" % (str(num_robots), str(num_servicemen), \
                str(num_nuts), str(num_spanners), str(num_toolboxes))

    with open(name+'.pddl', 'w') as f:
        f.write(pddl_str)
        f.close()

    sys.exit(0)
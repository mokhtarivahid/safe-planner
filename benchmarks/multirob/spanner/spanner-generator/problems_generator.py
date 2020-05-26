#!/usr/bin/env python
import sys, random
import os, time

from spanner_generator import gen_problem

#*****************#
# MAIN
#*****************#
if __name__ == '__main__':

    max_robots = 2
    max_servicemen = 1
    max_nuts = 7
    max_spanners = 4
    max_toolboxes = 2

    for r in range(2,max_robots+1): 
      for m in range(1,max_servicemen+1): 
        for n in range(r,max_nuts+1): 
          for s in reversed(range(r,min(n, max_spanners)+1)): 
            for t in range(1,min(n, s, max_toolboxes)+1): 
                pddl_str = gen_problem(r, m, n, s, t)
                print(pddl_str)

                name="prob_%s_%s_%s_%s_%s" % (str(r), str(m), str(n), str(s), str(t))

                with open(name+'.pddl', 'w') as f:
                    f.write(pddl_str)
                    f.close()

    sys.exit(0)
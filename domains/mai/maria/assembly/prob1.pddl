(define (problem prob1)

  (:domain packaging)

  (:objects 
            left-arm right-arm - arm
            bin-cap bin-base package peg hole assembly-pose-left assembly-pose-right cap base - graspable
            )

  (:init 
            (package package)
            (hole hole)
            (peg peg)
            (cap cap)
            (base base)

            (assembly assembly-pose-left)
            (assembly assembly-pose-right)

            (arm_canreach left-arm bin-cap)
            (arm_canreach left-arm bin-base)
            (arm_canreach left-arm peg)
            (arm_canreach left-arm assembly-pose-left)

            (arm_canreach right-arm bin-cap)
            (arm_canreach right-arm bin-base)
            (arm_canreach right-arm hole)
            (arm_canreach right-arm assembly-pose-right)
            (arm_canreach right-arm package)

            (arm_free left-arm)
            (arm_free right-arm)

            (object_in cap bin-cap)
            (object_in base bin-base)

            (arm_at left-arm bin-base)
            (arm_at right-arm bin-cap)

            (free package)
            (free hole)
            (free peg)
            (free cap)
            (free base)
            (free assembly-pose-left)
            (free assembly-pose-right)
            )

  (:goal (and
            (assembled cap base)
            (packed cap base package)
          ))

)
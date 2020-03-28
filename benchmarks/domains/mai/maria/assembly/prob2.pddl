(define (problem prob3)

  (:domain packaging)

  (:objects 
            left-arm right-arm - arm
            bin-cap bin-base package peg hole assembly-pose-left assembly-pose-right cap1 cap2 base1 base2 - graspable
            )

  (:init 
            (package package)
            (hole hole)
            (peg peg)
            (cap cap1)
            (cap cap2)
            (base base1)
            (base base2)

            (assembly assembly-pose-left)
            (assembly assembly-pose-right)

            (arm_canreach left-arm bin-base)
            (arm_canreach left-arm peg)
            (arm_canreach left-arm assembly-pose-left)

            (arm_canreach right-arm bin-cap)
            (arm_canreach right-arm hole)
            (arm_canreach right-arm assembly-pose-right)
            (arm_canreach right-arm package)

            (arm_free left-arm)
            (arm_free right-arm)

            (object_in cap1 bin-cap)
            (object_in cap2 bin-cap)
            (object_in base1 bin-base)
            (object_in base2 bin-base)

            (arm_at left-arm bin-base)
            (arm_at right-arm bin-cap)

            (free package)
            (free hole)
            (free peg)
            (free cap1)
            (free cap2)
            (free base1)
            (free base2)
            (free assembly-pose-left)
            (free assembly-pose-right)
            )

  (:goal (and
            (assembled cap1 base1)
            (assembled cap2 base2)
            (packed cap1 base1 package)
            (packed cap2 base2 package)
          ))

)
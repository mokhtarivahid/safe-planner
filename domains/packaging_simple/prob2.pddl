(define (problem prob0)

  (:domain packaging)

  (:objects 
            left-arm right-arm - arm
            bin-cap bin-base package peg hole camera assembly-pose-left assembly-pose-right cap1 cap2 cap3 base1 base2 base3 - graspable
            )

  (:init 
            (package package)
            (hole hole)
            (peg peg)
            (camera camera)
            (cap cap1)
            (cap cap2)
            (cap cap3)
            (base base1)
            (base base2)
            (base base3)

            (unknown_orientation cap1)
            (unknown_orientation cap2)
            (unknown_orientation cap3)
            (unknown_orientation base1)
            (unknown_orientation base2)
            (unknown_orientation base3)

            (assembly assembly-pose-left)
            (assembly assembly-pose-right)

            ; (arm_canreach left-arm bin-cap)
            (arm_canreach left-arm bin-base)
            (arm_canreach left-arm peg)
            (arm_canreach left-arm camera)
            (arm_canreach left-arm assembly-pose-left)

            (arm_canreach right-arm bin-cap)
            ; (arm_canreach right-arm bin-base)
            (arm_canreach right-arm hole)
            (arm_canreach right-arm camera)
            (arm_canreach right-arm assembly-pose-right)
            (arm_canreach right-arm package)

            (arm_free left-arm)
            (arm_free right-arm)

            (object_in cap1 bin-cap)
            (object_in cap2 bin-cap)
            (object_in cap3 bin-cap)
            (object_in base1 bin-base)
            (object_in base2 bin-base)
            (object_in base3 bin-base)

            (arm_at left-arm bin-base)
            (arm_at right-arm bin-cap)

            (free package)
            (free hole)
            (free peg)
            (free camera)
            (free cap1)
            (free cap2)
            (free cap3)
            (free base1)
            (free base2)
            (free base3)
            (free assembly-pose-left)
            (free assembly-pose-right)
            )

  (:goal (and
            (assembled cap1 base1)
            (assembled cap2 base2)
            (assembled cap3 base3)
            (packed cap1 base1 package)
            (packed cap2 base2 package)
            (packed cap3 base3 package)
          ))

)
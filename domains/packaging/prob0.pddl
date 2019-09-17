(define (problem prob0)

  (:domain packaging)

  (:objects 
            left-arm right-arm - arm
            bin-top bin-base package peg hole camera assembly-pose-left assembly-pose-right top base - object
            )

  (:init 
            (package package)
            (hole hole)
            (peg peg)
            (camera camera)
            (top top)
            (base base)

            (assembly assembly-pose-left)
            (assembly assembly-pose-right)

            (arm_canreach left-arm bin-top)
            (arm_canreach left-arm bin-base)
            ; (arm_canreach left-arm hole)
            (arm_canreach left-arm peg)
            ; (arm_canreach left-arm top)
            ; (arm_canreach left-arm base)
            (arm_canreach left-arm camera)
            (arm_canreach left-arm assembly-pose-left)
            ; (arm_canreach left-arm package)

            (arm_canreach right-arm bin-top)
            (arm_canreach right-arm bin-base)
            (arm_canreach right-arm hole)
            ; (arm_canreach right-arm peg)
            ; (arm_canreach right-arm top)
            ; (arm_canreach right-arm base)
            (arm_canreach right-arm camera)
            (arm_canreach right-arm assembly-pose-right)
            (arm_canreach right-arm package)

            (arm_free left-arm)
            (arm_free right-arm)

            (object_in top bin-top)
            (object_in base bin-base)

            (arm_at left-arm bin-base)
            (arm_at right-arm bin-top)

            (free package)
            (free hole)
            (free peg)
            (free camera)
            (free top)
            (free base)
            (free assembly-pose-left)
            (free assembly-pose-right)
            )

  (:goal (and
            (assembled top base)
            (packed top base package)
          ))

)
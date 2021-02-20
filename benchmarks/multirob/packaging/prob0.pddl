(define (problem prob0)

  (:domain packaging)

  (:objects 
            left_arm right_arm - arm
            bin_cap bin_base package camera cap base - graspable
            )

  (:init 
            (package package)
            (camera camera)

            (unknown_orientation cap)
            (unknown_orientation base)

            (arm_canreach left_arm bin_cap)
            (arm_canreach left_arm bin_base)
            (arm_canreach left_arm camera)
            (arm_canreach left_arm package)

            (arm_canreach right_arm bin_cap)
            (arm_canreach right_arm bin_base)
            (arm_canreach right_arm camera)
            (arm_canreach right_arm package)

            (arm_free left_arm)
            (arm_free right_arm)

            (object_in cap bin_cap)
            (object_in base bin_base)

            (arm_at left_arm bin_base)
            (arm_at right_arm bin_cap)

            (free package)
            (free camera)
            (free cap)
            (free base)
            )

  (:goal (and
            (packed cap package)
            (packed base package)
            (arm_at left_arm package)
            ; (gripped left_arm cap)
            ; (upward cap)
            (arm_at right_arm package)
            ; (gripped right_arm base)
            ; (upward base)
          ))

)
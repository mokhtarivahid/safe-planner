(define (problem prob0)

  (:domain packaging)

  (:objects 
            left_arm right_arm - arm
            bin_cap bin_base package peg hole camera assembly_pose_left assembly_pose_right cap base - graspable
            )

  (:init 
            (package package)
            (hole hole)
            (peg peg)
            (camera camera)
            (cap cap)
            (base base)

            (unknown_orientation cap)
            (unknown_orientation base)

            (assembly assembly_pose_left)
            (assembly assembly_pose_right)

            (arm_canreach left_arm bin_cap)
            (arm_canreach left_arm bin_base)
            ; (arm_canreach left_arm hole)
            (arm_canreach left_arm peg)
            ; (arm_canreach left_arm cap)
            ; (arm_canreach left_arm base)
            (arm_canreach left_arm camera)
            (arm_canreach left_arm assembly_pose_left)
            ; (arm_canreach left_arm package)

            (arm_canreach right_arm bin_cap)
            (arm_canreach right_arm bin_base)
            (arm_canreach right_arm hole)
            ; (arm_canreach right_arm peg)
            ; (arm_canreach right_arm cap)
            ; (arm_canreach right_arm base)
            (arm_canreach right_arm camera)
            (arm_canreach right_arm assembly_pose_right)
            (arm_canreach right_arm package)

            (arm_free left_arm)
            (arm_free right_arm)

            (object_in cap bin_cap)
            (object_in base bin_base)

            (arm_at left_arm bin_base)
            (arm_at right_arm bin_cap)

            (free package)
            (free hole)
            (free peg)
            (free camera)
            (free cap)
            (free base)
            (free assembly_pose_left)
            (free assembly_pose_right)
            )

  (:goal (and
            (assembled cap base)
            ; (packed cap base package)
          ))

)
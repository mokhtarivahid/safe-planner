(define (problem prob0)

  (:domain pickit)

  (:objects 
            arm1 arm2 - arm
            box1 box2 package1 - container
            part1 part2 - graspable
            assembly_pose1 assembly_pose2 - assemble)

  (:init 
            (arm_canreach arm1 box1)
            ; (arm_canreach arm1 box2)
            (arm_canreach arm1 assembly_pose1)
            (arm_canreach arm1 package1)

            ; (arm_canreach arm2 box1)
            (arm_canreach arm2 box2)
            (arm_canreach arm2 assembly_pose2)
            ; (arm_canreach arm2 package1)

            (arm_free arm1)
            (arm_free arm2)

            (object_in part1 box1)
            (object_in part2 box2)

            (arm_at arm1 box1)
            (arm_at arm2 box2)

            ; (free box1)
            ; (free box2)
            (free package1)
            (free assembly_pose1)
            (free assembly_pose2)
            )

  (:goal (and
            (packed part1 part2 package1)
          ))
)
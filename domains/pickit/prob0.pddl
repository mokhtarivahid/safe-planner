(define (problem prob0)

  (:domain pickit)

  (:objects 
            arm1 arm2 - arm
            camera1 
            box1 box2 peg1 hole1 package1 
            cap1 base1 
            assembly_pose1 assembly_pose2 - object)

  (:init 
            (arm arm1)
            (arm arm2)
            (box box1)
            (box box2)
            (package package1)
            (hole hole1)
            (peg peg1)
            (camera camera1)
            (cap cap1)
            (base base1)
            (unknown_pos cap1)
            (unknown_pos base1)
            (pose assembly_pose1)
            (pose assembly_pose2)
            
            (graspable cap1)
            (graspable base1)
            
            (arm_canreach arm1 box1)
            (arm_canreach arm1 box2)
            (arm_canreach arm1 hole1)
            (arm_canreach arm1 peg1)
            (arm_canreach arm1 cap1)
            (arm_canreach arm1 base1)
            (arm_canreach arm1 camera1)
            (arm_canreach arm1 assembly_pose1)
            (arm_canreach arm1 package1)

            (arm_canreach arm2 box1)
            (arm_canreach arm2 box2)
            (arm_canreach arm2 hole1)
            (arm_canreach arm2 peg1)
            (arm_canreach arm2 cap1)
            (arm_canreach arm2 base1)
            (arm_canreach arm2 camera1)
            (arm_canreach arm2 assembly_pose2)
            (arm_canreach arm2 package1)

            ; (co_arms arm1 arm2)

            (arm_free arm1)
            (arm_free arm2)

            (object_in cap1 box1)
            (object_in base1 box2)

            (arm_at arm1 box1)
            (arm_at arm2 box2)

            (in_use box1)
            (in_use box2)

            (free package1)
            (free hole1)
            (free peg1)
            (free camera1)
            (free cap1)
            (free base1)
            (free assembly_pose1)
            (free assembly_pose2)

            )

  (:goal (and
            (packed cap1 base1 package1)
          ))
  ; (:metric minimize (total-cost))
)
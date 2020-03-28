(define (problem prob0)

  (:domain pickit)

  (:objects 
            arm1 arm2 - arm
            box1 box2 peg1 hole1 camera1 package1 
            cap1 cap2 base1 base2 - object)

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
            (cap cap2)
            (base base1)
            (base base2)
            
            (graspable cap1)
            (graspable cap2)
            (graspable base1)
            (graspable base2)
            
            (arm_canreach arm1 box1)
            (arm_canreach arm1 box2)
            (arm_canreach arm1 hole1)
            (arm_canreach arm1 peg1)
            (arm_canreach arm1 cap1)
            (arm_canreach arm1 cap2)
            (arm_canreach arm1 base1)
            (arm_canreach arm1 base2)
            (arm_canreach arm1 camera1)
            (arm_canreach arm1 package1)

            (arm_canreach arm2 box1)
            (arm_canreach arm2 box2)
            (arm_canreach arm2 hole1)
            (arm_canreach arm2 peg1)
            (arm_canreach arm2 cap1)
            (arm_canreach arm2 cap2)
            (arm_canreach arm2 base1)
            (arm_canreach arm2 base2)
            (arm_canreach arm2 camera1)
            (arm_canreach arm2 package1)

            (co_arms arm1 arm2)

            (arm_free arm1)
            (arm_free arm2)

            (object_in cap1 box1)
            (object_in cap2 box1)
            (object_in base1 box2)
            (object_in base2 box2)

            (arm_at arm1 box1)
            (arm_at arm2 box2)

            (occupied box1)
            (occupied box2)

            (free package1)
            (free hole1)
            (free peg1)
            (free camera1)
            (free cap1)
            (free cap2)
            (free base1)
            (free base2)
            )

  (:goal (and
             (object_in cap1 package1)
             (object_in cap2 package1)
             (object_in base1 package1)
             (object_in base2 package1)
         ))

)
(define (problem prob1)
(:domain tabletop)
(:objects 
          left-arm right-arm - arm
          table1 - table
          tray1 - tray
          object1 object2 object3 - object
          obj1_gpt obj1_gpl obj1_gpr 
          obj2_gpt obj2_gpl obj2_gpr 
          obj3_gpt obj3_gpl obj3_gpr  - grasp_pose)

(:init 
          (free left-arm)
          (free right-arm)

          (ontable object1 table1)
          (ontable object2 table1)
          (ontable object3 table1)

          (filled object1)
          (filled object2)
          (empty object3)

          (graspable object1 obj1_gpt)
          (graspable object1 obj1_gpl)
          (graspable object1 obj1_gpr)
          (graspable object2 obj2_gpt)
          (graspable object2 obj2_gpl)
          (graspable object2 obj2_gpr)
          (graspable object3 obj3_gpt)
          (graspable object3 obj3_gpl)
          (graspable object3 obj3_gpr)

          (reachable left-arm obj1_gpt)
          (reachable left-arm obj1_gpl)
          (reachable left-arm obj2_gpt)
          (reachable left-arm obj2_gpl)
          (reachable left-arm obj3_gpt)
          (reachable left-arm obj3_gpl)

          (reachable right-arm obj1_gpt)
          (reachable right-arm obj1_gpr)
          (reachable right-arm obj2_gpt)
          (reachable right-arm obj2_gpr)
          (reachable right-arm obj3_gpt)
          (reachable right-arm obj3_gpr)


          ; (obstructed obj1_gpl obj2)
          ; ; (obstructed obj2_gpr obj1)
          ; (obstructed obj1_gpr obj3)
          ; ; (obstructed obj3_gpl obj1)

          (unobstructed obj1_gpt)
          (unobstructed obj1_gpl)
          (unobstructed obj1_gpr)
          (unobstructed obj2_gpt)
          (unobstructed obj2_gpl)
          (unobstructed obj2_gpr)
          (unobstructed obj3_gpt)
          (unobstructed obj3_gpl)
          (unobstructed obj3_gpr)
          )

(:goal  (and
          (ontray object1 tray1)
          (filled object1)
        ))
)
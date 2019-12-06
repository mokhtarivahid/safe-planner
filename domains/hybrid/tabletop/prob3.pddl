(define (problem prob1)
(:domain tabletop)
(:objects 
          left-arm right-arm - arm
          table1 - table
          tray1 - tray
          obj1 obj2 obj3 obj4 obj5 
          ; obj6 obj7 
          ; obj8 
          - object
          obj1_gpt obj1_gpl obj1_gpr 
          obj2_gpt obj2_gpl obj2_gpr 
          obj3_gpt obj3_gpl obj3_gpr  
          obj4_gpt obj4_gpl obj4_gpr 
          obj5_gpt obj5_gpl obj5_gpr 
          ; obj6_gpt obj6_gpl obj6_gpr 
          ; obj7_gpt obj7_gpl obj7_gpr 
          ; ; obj8_gpt obj8_gpl obj8_gpr 
          - grasp_pose)

(:init 
          (free left-arm)
          (free right-arm)

          (ontable obj1 table1)
          (ontable obj2 table1)
          (ontable obj3 table1)
          (ontable obj4 table1)
          (ontable obj5 table1)
          ; (ontable obj6 table1)
          ; (ontable obj7 table1)
          ; ; (ontable obj8 table1)

          (graspable obj1 obj1_gpt)
          (graspable obj1 obj1_gpl)
          (graspable obj1 obj1_gpr)
          (graspable obj2 obj2_gpt)
          (graspable obj2 obj2_gpl)
          (graspable obj2 obj2_gpr)
          (graspable obj3 obj3_gpt)
          (graspable obj3 obj3_gpl)
          (graspable obj3 obj3_gpr)
          (graspable obj4 obj4_gpt)
          (graspable obj4 obj4_gpl)
          (graspable obj4 obj4_gpr)
          (graspable obj5 obj5_gpt)
          (graspable obj5 obj5_gpl)
          (graspable obj5 obj5_gpr)
          ; (graspable obj6 obj6_gpt)
          ; (graspable obj6 obj6_gpl)
          ; (graspable obj6 obj6_gpr)
          ; (graspable obj7 obj7_gpt)
          ; (graspable obj7 obj7_gpl)
          ; (graspable obj7 obj7_gpr)
          ; (graspable obj8 obj8_gpt)
          ; (graspable obj8 obj8_gpl)
          ; (graspable obj8 obj8_gpr)

          (reachable left-arm obj1_gpt)
          (reachable left-arm obj1_gpl)
          (reachable left-arm obj2_gpt)
          (reachable left-arm obj2_gpl)
          (reachable left-arm obj3_gpt)
          (reachable left-arm obj3_gpl)
          (reachable left-arm obj4_gpt)
          (reachable left-arm obj4_gpl)
          (reachable left-arm obj5_gpt)
          (reachable left-arm obj5_gpl)
          ; (reachable left-arm obj6_gpt)
          ; (reachable left-arm obj6_gpl)
          ; (reachable left-arm obj7_gpt)
          ; (reachable left-arm obj7_gpl)
          ; (reachable left-arm obj8_gpt)
          ; (reachable left-arm obj8_gpl)

          (reachable right-arm obj1_gpt)
          (reachable right-arm obj1_gpr)
          (reachable right-arm obj2_gpt)
          (reachable right-arm obj2_gpr)
          (reachable right-arm obj3_gpt)
          (reachable right-arm obj3_gpr)
          (reachable right-arm obj4_gpt)
          (reachable right-arm obj4_gpr)
          (reachable right-arm obj5_gpt)
          (reachable right-arm obj5_gpr)
          ; (reachable right-arm obj6_gpt)
          ; (reachable right-arm obj6_gpr)
          ; (reachable right-arm obj7_gpt)
          ; (reachable right-arm obj7_gpr)
          ; (reachable right-arm obj8_gpt)
          ; (reachable right-arm obj8_gpr)

          (filled obj1)
          (filled obj2)
          (filled obj3)
          (filled obj4)
          (empty obj5)
          ; (filled obj6)
          ; (filled obj7)
          ; (empty obj8)

          (obstructed obj1_gpl obj2)
          (obstructed obj2_gpr obj1)
          (obstructed obj1_gpl obj5)
          (obstructed obj5_gpr obj1)
          (obstructed obj1_gpr obj3)
          (obstructed obj3_gpl obj1)
          (obstructed obj1_gpr obj4)
          (obstructed obj4_gpl obj1)


          (unobstructed obj1_gpt)
          ; (unobstructed obj1_gpl)
          ; (unobstructed obj1_gpr)
          (unobstructed obj2_gpt)
          (unobstructed obj2_gpl)
          ; (unobstructed obj2_gpr)
          (unobstructed obj3_gpt)
          ; (unobstructed obj3_gpl)
          (unobstructed obj3_gpr)
          (unobstructed obj4_gpt)
          ; (unobstructed obj4_gpl)
          (unobstructed obj4_gpr)
          (unobstructed obj5_gpt)
          (unobstructed obj5_gpl)
          ; (unobstructed obj5_gpr)
          ; (unobstructed obj6_gpt)
          ; (unobstructed obj6_gpl)
          ; (unobstructed obj6_gpr)
          ; (unobstructed obj7_gpt)
          ; (unobstructed obj7_gpl)
          ; (unobstructed obj7_gpr)
          ; (unobstructed obj8_gpt)
          ; (unobstructed obj8_gpl)
          ; (unobstructed obj8_gpr)
          )

(:goal  (and
          ; (unobstructed obj1_gpl)
          (co_lifted obj1)
          ; (ontray obj1 tray1)
          ; (filled obj1)
          ; (ontray obj2 tray1)
          ; (filled obj2)
          ; (ontray obj3 tray1)
          ; (empty obj3)
          ; (lifted obj3)
          ; (lifted obj4)

          (filled obj1)
          (filled obj2)
          (filled obj3)
          (filled obj4)
          ; (empty obj5)
          ; (filled obj6)
          ; (filled obj7)

        ))
)
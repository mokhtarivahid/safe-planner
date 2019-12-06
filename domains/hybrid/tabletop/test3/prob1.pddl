(define (problem prob1)
(:domain tabletop)
(:objects 
          left-arm right-arm - arm
          table1 - table
          tray1 - tray
          obj1 obj2 - object
          obj1_gpt obj1_gpl obj1_gpr 
          obj2_gpt obj2_gpl obj2_gpr 
          - grasp_pose)

(:init 
          (free left-arm)
          (free right-arm)

          (ontable obj1 table1)
          (ontable obj2 table1)

          (empty obj1)
          (empty obj2)

          (graspable obj1 obj1_gpt)
          (graspable obj1 obj1_gpl)
          (graspable obj1 obj1_gpr)
          (graspable obj2 obj2_gpt)
          (graspable obj2 obj2_gpl)
          (graspable obj2 obj2_gpr)

          (reachable left-arm obj1_gpt)
          (reachable left-arm obj1_gpl)
          (reachable left-arm obj2_gpt)
          (reachable left-arm obj2_gpl)

          (reachable right-arm obj1_gpt)
          (reachable right-arm obj1_gpr)
          (reachable right-arm obj2_gpt)
          (reachable right-arm obj2_gpr)

          (ungrasped obj1_gpt)
          (ungrasped obj1_gpl)
          (ungrasped obj1_gpr)
          (ungrasped obj2_gpt)
          (ungrasped obj2_gpl)
          (ungrasped obj2_gpr)

          (obstructed obj1_gpr obj2)
          (obstructed obj2_gpl obj1)
          ; (obstructed obj1_gpr obj3)
          ; (obstructed obj3_gpl obj1)

          ; (unobstructed obj1_gpt)
          ; (unobstructed obj1_gpl)
          ; (unobstructed obj1_gpr)
          ; (unobstructed obj2_gpt)
          ; (unobstructed obj2_gpl)
          ; (unobstructed obj2_gpr)
          ; (unobstructed obj3_gpt)
          ; (unobstructed obj3_gpl)
          ; (unobstructed obj3_gpr)
          )

(:goal  (and
          (grasped right-arm obj1 obj1_gpr)
          (grasped left-arm obj1 obj1_gpl)
          (lifted obj1)
          ; (holding obj2)
          ; (ontray obj1 tray1)
          ; (empty obj1)
          ; (ontray obj2 tray1)
          ; (ontray obj3 tray1)
        ))
)
(define (problem prob1)
(:domain tabletop)
(:objects 
          arm1 arm2 - arm
          table1 - table
          tray1 - tray
          obj1 obj2 - object
          obj1_gpt obj1_gpl obj1_gpr 
          obj2_gpt obj2_gpl obj2_gpr  - grasp_pose)

(:init 
          ; (free arm1)
          ; (free arm2)

          (ontable obj1 table1)
          ; (ontable obj2 table1)

          (grasped arm1 obj2 obj2_gpl)
          (grasped arm2 obj2 obj2_gpr)
          (holding obj2)          

          (empty obj1)
          (filled obj2)

          (graspable obj1 obj1_gpt)
          (graspable obj1 obj1_gpl)
          (graspable obj1 obj1_gpr)
          (graspable obj2 obj2_gpt)
          ; (graspable obj2 obj2_gpl)
          ; (graspable obj2 obj2_gpr)

          (reachable arm1 obj1_gpt)
          (reachable arm1 obj1_gpl)
          (reachable arm1 obj1_gpr)
          (reachable arm1 obj2_gpt)
          (reachable arm1 obj2_gpl)
          (reachable arm1 obj2_gpr)

          (reachable arm2 obj1_gpt)
          (reachable arm2 obj1_gpl)
          (reachable arm2 obj1_gpr)
          (reachable arm2 obj2_gpt)
          (reachable arm2 obj2_gpl)
          (reachable arm2 obj2_gpr)

          (unobstructed obj1_gpt)
          (unobstructed obj1_gpl)
          (unobstructed obj1_gpr)
          (unobstructed obj2_gpt)
          (unobstructed obj2_gpl)
          (unobstructed obj2_gpr)
          )

(:goal  (and
          ; (holding obj1)
          ; (holding obj2)
          ; (ontable obj2 table1)
          (ontray obj2 tray1)
          (free arm1)
          (free arm2)
        ))
)
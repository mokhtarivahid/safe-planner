(define (problem prob0)
(:domain solenoid)
(:objects hole1 - hole
          sole1 - solenoid)
(:init 
       (on sole1 hole1)
       ; (no_human_at sole1)
       ; (no_human_at sole2)
       ; (gripper_free)
       (robot_at_base)
       )
(:goal 
  (and 
       ; (robot_at sole1)
       (removed sole1)
       ; (removed sole2 hole2)
       ; (ontable sole1)
       ; (ontable sole2)
  ))
)

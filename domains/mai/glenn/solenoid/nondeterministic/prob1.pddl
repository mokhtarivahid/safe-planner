(define (problem prob0)
(:domain solenoid)
(:objects hole1 hole2 - hole
          sole1 sole2 - solenoid)
(:init 
       (on sole1 hole1)
       (on sole2 hole2)
       (no_human_at sole1)
       (no_human_at sole2)
       (gripper_free)
       (robot_at_base)
       )
(:goal 
  (and 
        (removed sole1 hole1)
        (removed sole2 hole2)
        ; (ontable sole1)
        ; (ontable sole2)
  ))
)

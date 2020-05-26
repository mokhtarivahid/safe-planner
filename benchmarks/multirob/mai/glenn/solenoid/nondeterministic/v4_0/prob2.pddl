(define (problem prob2)
(:domain solenoid)
(:objects sole1 sole2 sole3 - solenoid)
(:init 
       (sense sole1) 
       (sense sole2) 
       (sense sole3) 
       (observe_state)
       (gripper_free)
       (robot_at_home))
(:goal 
  (and 
        (removed sole1)
        (removed sole2)
        (removed sole3)))
)

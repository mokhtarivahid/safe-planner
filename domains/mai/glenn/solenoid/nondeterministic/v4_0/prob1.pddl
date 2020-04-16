(define (problem prob1)
(:domain solenoid)
(:objects sole1 sole2 - solenoid)
(:init 
       (sense sole1) 
       (sense sole2) 
       (observe_state)
       (gripper_free)
       (robot_at_home))
(:goal 
  (and 
        (removed sole1)
        (removed sole2)))
)

(define (problem prob0)
(:domain solenoid)
(:objects hole1 hole2 hole3 - hole
          sole1 sole2 sole3 - solenoid)
(:init 
       (on sole1 hole1)
       (on sole2 hole2)
       (on sole3 hole3)
       (gripper_free)
       (robot_at_home)
       (state_observation_needed))
(:goal 
  (and 
        (removed sole1)
        (removed sole2)
        (removed sole3)))
)

(define (problem prob0)
(:domain solenoid)
(:objects hole1 hole2 - hole
          sole1 sole2 - solenoid)
(:init 
       (on sole1 hole1)
       (on sole2 hole2)
       (gripper_free)
       (robot_at_home)
       (state_observation_needed))
(:goal 
  (and 
        (removed sole1)
        (removed sole2)))
)

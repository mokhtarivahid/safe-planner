(define (problem prob0)
(:domain solenoid)
(:objects hole1 hole2 - hole
          sole1 - solenoid)
(:init 
       (on sole1 hole1)
       (gripper_free)
       (robot_at_home)
       (state_observation_needed)
       )
(:goal (removed sole1))
)

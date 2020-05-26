(define (problem prob0)
(:domain solenoid)
(:objects sole1 - solenoid)
(:init 
       (sense sole1) 
       (observe_state)
       (gripper_free))
(:goal (removed sole1))
)

(define (problem prob0)
(:domain solenoid)
(:objects sole1 sole2 - solenoid)
(:init 
       (ontable sole1)
       (ontable sole2)
       (gripper_free)
       (robot_at_home))
(:goal 
  (and 
        (removed sole1)
        (removed sole2)))
)

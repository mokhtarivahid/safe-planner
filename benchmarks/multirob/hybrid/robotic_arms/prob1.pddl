(define (problem prob1)
(:domain robotic-arms)
(:objects 
          arm1 arm2 - robot
          table1 - table
          crate1 - crate
          bottle1 bottle2 bottle3 - object)

(:init 
          (arm arm1)
          (arm arm2)
          (table table1)
          (crate crate1)
          
          (arm_canreach arm1 bottle1)
          (arm_canreach arm1 bottle2)
          (arm_canreach arm1 bottle3)

          (arm_canreach arm2 bottle1)
          (arm_canreach arm2 bottle2)
          (arm_canreach arm2 bottle3)

          (arm_free arm1)
          (arm_free arm2)

          (on bottle1 table1)
          (on bottle2 table1)
          (on bottle3 table1)

          (blocked bottle1 bottle2)
          (blocked bottle2 bottle3)

          (clear bottle3)
          )

(:goal  (and
          (in bottle1 crate1)
          (in bottle2 crate1)
        ))
)
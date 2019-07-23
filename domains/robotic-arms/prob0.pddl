(define (problem prob0)
(:domain robotic-arms)
(:objects 
          arm1 arm2 - robot
          table1 - table
          crate1 - crate
          bottle1 bottle2 bottle3 bottle4 bottle5 
          bottle6 bottle7 bottle8 bottle9 bottle10 - object)

(:init 
          (arm arm1)
          (arm arm2)
          (table table1)
          (crate crate1)
          
          (arm_canreach arm1 bottle1)
          (arm_canreach arm1 bottle2)
          (arm_canreach arm1 bottle3)
          (arm_canreach arm1 bottle4)
          (arm_canreach arm1 bottle5)
          (arm_canreach arm1 bottle6)
          (arm_canreach arm1 bottle7)
          (arm_canreach arm1 bottle8)
          (arm_canreach arm1 bottle9)
          (arm_canreach arm1 bottle10)

          (arm_canreach arm2 bottle1)
          (arm_canreach arm2 bottle2)
          (arm_canreach arm2 bottle3)
          (arm_canreach arm2 bottle4)
          (arm_canreach arm2 bottle5)
          (arm_canreach arm2 bottle6)
          (arm_canreach arm2 bottle7)
          (arm_canreach arm2 bottle8)
          (arm_canreach arm2 bottle9)
          (arm_canreach arm2 bottle10)

          (arm_free arm1)
          (arm_free arm2)

          (on bottle1 table1)
          (on bottle2 table1)
          (on bottle3 table1)
          (on bottle4 table1)
          (on bottle5 table1)
          (on bottle6 table1)
          (on bottle7 table1)
          (on bottle8 table1)
          (on bottle9 table1)
          (on bottle10 table1)

          ; (clear bottle1)
          ; (clear bottle2)
          (clear bottle3)
          (clear bottle4)
          (clear bottle5)
          (clear bottle6)
          (clear bottle7)
          (clear bottle8)
          (clear bottle9)
          (clear bottle10)

          (blocked bottle1 bottle2)
          (blocked bottle2 bottle3)
          )

(:goal  (and
          (in bottle1 crate1)
          (in bottle2 crate1)
          (in bottle3 crate1)
          (in bottle4 crate1)
          (in bottle5 crate1)
          (in bottle6 crate1)
          (in bottle7 crate1)
          (in bottle8 crate1)
          (in bottle9 crate1)
          (in bottle10 crate1)
        ))
)
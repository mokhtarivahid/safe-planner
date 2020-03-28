(define (problem prob0)

  (:domain pickit)

  (:objects 
            arm1 arm2 - arm
            camera1 
            bin1 bin2 stand1 stand2 box1 
            product1 product2 - object)

  (:init 
            (arm arm1)
            (arm arm2)
            (bin bin1)
            (bin bin2)
            (package box1)
            (stand stand2)
            (stand stand1)
            (camera camera1)
            (product product1)
            (product product2)
            
            (graspable product1)
            (graspable product2)
            
            (arm_canreach arm1 bin1)
            (arm_canreach arm1 bin2)
            (arm_canreach arm1 stand1)
            ; (arm_canreach arm1 stand2)
            (arm_canreach arm1 product1)
            (arm_canreach arm1 product2)
            (arm_canreach arm1 camera1)
            (arm_canreach arm1 box1)

            (arm_canreach arm2 bin1)
            (arm_canreach arm2 bin2)
            ; (arm_canreach arm2 stand1)
            (arm_canreach arm2 stand2)
            (arm_canreach arm2 product1)
            (arm_canreach arm2 product2)
            (arm_canreach arm2 camera1)
            (arm_canreach arm2 box1)

            (arm_free arm1)
            (arm_free arm2)

            (object_in product1 bin1)
            (object_in product2 bin2)

            (arm_at arm1 bin1)
            (arm_at arm2 bin2)

            (occupied bin1)
            (occupied bin2)

            (free box1)
            (free stand2)
            (free stand1)
            (free camera1)
            (free product1)
            (free product2)

            )

  (:goal (and
            (object_in product1 box1)
            (object_in product2 box1)
          ))
  ; (:metric minimize (total-cost))
)
(define (problem prob0)

  (:domain packaging)

  (:objects 
            left-arm right-arm - arm
            ; surface-left surface-right ; - surface
            _handover-left _handover-right ; - space
            bin ; - container
            package ; - package
            camera ; - camera
            obj1 obj2 - location ; - graspable
            )

  (:init 
            ;; location
            (arm left-arm)
            (arm right-arm)
            ; (surface surface-left)
            ; (surface surface-right)
            (space _handover-left)
            (space _handover-right)
            (container bin)
            (package package)
            (camera camera)

            ;; graspable
            (graspable obj1)
            (graspable obj2)

            ;; arm_canreach
            (arm_canreach left-arm _handover-left)
            ; (arm_canreach left-arm surface-left)
            (arm_canreach left-arm bin)
            (arm_canreach left-arm camera)
            (arm_canreach left-arm package)
            (arm_canreach left-arm obj1)
            (arm_canreach left-arm obj2)

            (arm_canreach right-arm _handover-right)
            ; (arm_canreach right-arm surface-right)
            (arm_canreach right-arm bin)
            (arm_canreach right-arm camera)
            (arm_canreach right-arm package)
            (arm_canreach right-arm obj1)
            (arm_canreach right-arm obj2)

            ;; arm_free
            (arm_free left-arm)
            (arm_free right-arm)

            ;; arm_at
            (arm_at left-arm _handover-left)
            (arm_at right-arm _handover-right)

            ;; object_in
            (object_in obj1 bin)
            (object_in obj2 bin)

            ;; location free state
            ; (location_free surface-left)
            ; (location_free surface-right)
            (location_free bin)
            (location_free package)
            (location_free camera)
            (location_free obj1)
            (location_free obj2)

            ;; obstruction state
            ; (blocked obj1 obj2)
            (unblocked obj1)
            (unblocked obj2)

            ;; improper grasp pose
            ; (improper_grasp right-arm obj1)
            )

  (:goal (and
            (packed obj1 package)
            (packed obj2 package)
          ))

)
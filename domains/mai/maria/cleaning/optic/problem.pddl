(define (problem prob0)
(:domain packaging)
(:objects left-arm right-arm - arm
          crate1 - container
          standby-left standby-right - location
          table1 - table
          obj1 obj2 obj3 obj4 - graspable)
;;; <<for optic planner (since the typed objects is not fully supported)>>
; (:objects left-arm right-arm - arm
;           crate1 table1 standby-left standby-right - location
;           obj1 obj2 obj3 obj4 - graspable)
(:init (arm_canreach left-arm table1)
       (arm_canreach left-arm crate1)
       (arm_canreach right-arm table1)
       (arm_canreach right-arm crate1)
       (arm_free left-arm)
       (arm_free right-arm)
       (on obj1 table1)
       (on obj3 table1)
       (on obj2 table1)
       (on obj4 table1)
       (arm_at left-arm standby-left)
       (arm_at right-arm standby-right)
       (location_free crate1)
       (location_free obj1)
       (location_free obj3)
       (location_free obj2)
       (location_free obj4))
(:goal (and (in obj1 crate1)
            (in obj3 crate1)
            (in obj2 crate1)
            (in obj4 crate1)
       ))
)

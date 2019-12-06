(define (problem prob0)
(:domain packaging)
(:objects left-arm right-arm - arm
          bin-cap bin-base package crate - container
          peg hole - location
          camera - camera
          assembly-pose-left assembly-pose-right - location
          cap1 base1 cap2 base2 - graspable)
(:init (package package)
       (hole hole)
       (peg peg)
       (crate crate)
       (camera camera)
       (cap cap1)
       (cap cap2)
       (base base1)
       (base base2)
       (assembly assembly-pose-left)
       (assembly assembly-pose-right)
       (arm_canreach left-arm bin-cap)
       (arm_canreach left-arm bin-base)
       (arm_canreach left-arm peg)
       (arm_canreach left-arm crate)
       (arm_canreach left-arm camera)
       (arm_canreach left-arm assembly-pose-left)
       (arm_canreach right-arm bin-cap)
       (arm_canreach right-arm bin-base)
       (arm_canreach right-arm hole)
       (arm_canreach right-arm crate)
       (arm_canreach right-arm camera)
       (arm_canreach right-arm assembly-pose-right)
       (arm_canreach right-arm package)
       (arm_free left-arm)
       (arm_free right-arm)
       (object_in cap1 bin-cap)
       (object_in cap2 bin-cap)
       (object_in base1 bin-base)
       (object_in base2 bin-base)
       (arm_at left-arm bin-cap)
       (arm_at right-arm bin-base)
       (free package)
       (free hole)
       (free peg)
       (free crate)
       (free camera)
       (free cap1)
       (free cap2)
       (free base1)
       (free base2)
       (free assembly-pose-left)
       (free assembly-pose-right))
(:goal (and (object_in cap1 crate)
            (object_in cap2 crate)
            (object_in base1 crate)
            (object_in base2 crate)
       ))
)

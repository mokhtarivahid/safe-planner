(define (problem prob2)
(:domain pickit)
(:objects 
      arm1 arm2 - arm
      assembly_pose1 assembly_pose2 - assembly
      box1 box2 package1 - container
      base1 base2 cap1 cap2 - graspable
      standby1 standby2 - standby)
(:init
      ;; arm1 configuration
      (arm_at arm1 standby1)
      (arm_canreach arm1 assembly_pose1)
      (arm_canreach arm1 box1)
      (arm_canreach arm1 package1)
      (arm_canreach arm1 standby1)
      (arm_free arm1)

      ;; arm2 configuration
      (arm_at arm2 standby2)
      (arm_canreach arm2 assembly_pose2)
      (arm_canreach arm2 box2)
      (arm_canreach arm2 standby2)
      (arm_free arm2)

      ;; locations
      (free assembly_pose1)
      (free assembly_pose2)
      (free box1)
      (free box2)
      (free package1)

      ;; objects
      (disassembled base1)
      (disassembled base2)
      (disassembled cap1)
      (disassembled cap2)
      (object_in base1 box2)
      (object_in base2 box2)
      (object_in cap1 box1)
      (object_in cap2 box1))
(:goal 
  (and
      (packed cap1 base1 package1)
      (packed cap2 base2 package1))))

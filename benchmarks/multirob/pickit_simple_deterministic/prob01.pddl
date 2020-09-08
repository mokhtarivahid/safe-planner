(define (problem prob1)
(:domain pickit)
(:objects 
      left_arm right_arm - arm
      base cap - graspable
      box_cap box_base package - container
      assembly_pos_left assembly_pos_right - assembly
      standby_left standby_right - standby)
(:init
      ;; left_arm configuration
      (arm_at left_arm standby_left)
      (arm_canreach left_arm assembly_pos_left)
      (arm_canreach left_arm box_cap)
      (arm_canreach left_arm package)
      (arm_canreach left_arm standby_left)
      (arm_free left_arm)

      ;; right_arm configuration
      (arm_at right_arm standby_right)
      (arm_canreach right_arm assembly_pos_right)
      (arm_canreach right_arm box_base)
      (arm_canreach right_arm standby_right)
      (arm_free right_arm)

      ;; locations
      (free assembly_pos_left)
      (free assembly_pos_right)
      (free box_cap)
      (free box_base)
      (free package)

      ;; objects
      (disassembled base)
      (disassembled cap)
      (object_in base box_base)
      (object_in cap box_cap))
(:goal 
      (assembled cap base)))
      ; (packed cap base package)))

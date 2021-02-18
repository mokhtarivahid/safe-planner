(define (problem p1)
(:domain solenoid)
(:objects left_arm right_arm - arm 
          rack1 rack2 - rack
          slot11 slot12 slot13 slot14 - slot
          slot21 slot22 slot23 slot24 - slot
          standby1 standby2 - slot
          solenoid1 solenoid2 solenoid3 solenoid4 - solenoid)
(:init
      ;; left_arm
      (arm_free left_arm)
      (arm_canreach left_arm standby1)
      (arm_canreach left_arm slot11)
      (arm_canreach left_arm slot12)
      (arm_canreach left_arm slot13)
      (arm_canreach left_arm slot14)
      (arm_canreach left_arm slot21)
      (arm_canreach left_arm slot22)
      (arm_canreach left_arm slot23)
      (arm_canreach left_arm slot24)

      ;; right_arm
      (arm_free right_arm)
      (arm_canreach right_arm standby2)
      (arm_canreach right_arm slot11)
      (arm_canreach right_arm slot12)
      (arm_canreach right_arm slot13)
      (arm_canreach right_arm slot14)
      (arm_canreach right_arm slot21)
      (arm_canreach right_arm slot22)
      (arm_canreach right_arm slot23)
      (arm_canreach right_arm slot24)

      ;; rack1
      (has_slot rack1 slot11)
      (has_slot rack1 slot12)
      (has_slot rack1 slot13)
      (has_slot rack1 slot14)
      (object_in solenoid1 slot11)
      (object_in solenoid2 slot12)
      (object_in solenoid3 slot13)
      (object_in solenoid4 slot14)
      (slot_free slot11) ;; no arm above slot
      (slot_free slot12)
      (slot_free slot13)
      (slot_free slot14)

      ;; rack2
      (has_slot rack2 slot21)
      (has_slot rack2 slot22)
      (has_slot rack2 slot23)
      (has_slot rack2 slot24)
      (slot_empty slot21) ;; no solenoid in slot
      (slot_empty slot22)
      (slot_empty slot23)
      (slot_empty slot24)
      (slot_free slot21) ;; no arm above slot
      (slot_free slot22)
      (slot_free slot23)
      (slot_free slot24)

      ;; initial robots positions
      (arm_above left_arm standby1)
      (arm_above right_arm standby2)

      ;; collision/admittance free status
      ; (collision_free left_arm)
      ; (collision_free right_arm)
      ; (admittance_free left_arm)
      ; (admittance_free right_arm)

      ;; collision detected
      (collision_detected left_arm)
      (collision_detected right_arm)
      (admittance_detected left_arm)
      (admittance_detected right_arm)

      )
(:goal 
  (and
      (object_in solenoid1 slot21)
      (object_in solenoid2 slot22)
      (object_in solenoid3 slot23)
      (object_in solenoid4 slot24)
      (arm_above left_arm standby1)
      (arm_above right_arm standby2)
      ))
)
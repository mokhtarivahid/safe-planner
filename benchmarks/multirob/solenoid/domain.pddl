;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Solenoid assembly domain
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(define (domain solenoid)

(:requirements :strips :typing)

(:types arm slot solenoid rack)

(:predicates
            (arm_free ?a - arm)
            (arm_canreach ?a - arm ?s - slot)
            (arm_above ?a - arm ?s - slot)
            (arm_at ?a - arm ?s - slot)
            (arm_gripping ?a - arm ?o - solenoid)
            (has_slot ?r - rack ?s - slot)
            (slot_free ?s - slot) ;; no arm at the slot
            (slot_empty ?s - slot) ;; no solenoid in the slot
            (object_in ?o - solenoid ?s - slot) ;; a solenoid in the slot
            (object_assembled ?o - solenoid ?r - rack) ;; a solenoid attached to the rack
            (collision_free ?a - arm)
            (collision_detected ?a - arm)
            (stop_collision_avoidance ?a - arm)
            (admittance_free ?a - arm)
            (admittance_detected ?a - arm)
            (stop_admittance_avoidance ?a - arm)
)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; avoid collision
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; (:durative-action avoid_collision
;  :parameters (?a - arm)
;  :duration (<= ?duration 1)
;  :condition (and (over all (collision_detected ?a))
;                  ; (at end (arm_above ?a ?s))
;                  (at end (stop_collision_avoidance ?a))
;                  )
;  :effect (and (at start (collision_free ?a))
;               (at end (collision_free ?a))
;               (at end (not (collision_detected ?a)))
;               (at end (not (stop_collision_avoidance ?a)))
;          )
;  )

(:action avoid_collision
 :parameters (?a - arm)
 :precondition (and (collision_detected ?a)
                 )
 :effect (and (collision_free ?a)
              (not (collision_detected ?a))
         )
 )

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; admittance (when a human appears)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; (:durative-action admittance_control
;  :parameters (?a - arm)
;  :duration (<= ?duration 1)
;  :condition (and (over all (admittance_detected ?a))
;                  ; (at end (arm_above ?a ?s))
;                  (at end (stop_admittance_avoidance ?a))
;                  )
;  :effect (and (at start (admittance_free ?a))
;               (at end (admittance_free ?a))
;               (at end (not (admittance_detected ?a)))
;               (at end (not (stop_admittance_avoidance ?a)))
;          )
;  )

(:action admittance_control
 :parameters (?a - arm)
 :precondition (and (admittance_detected ?a)
                 )
 :effect (and (admittance_free ?a)
              (not (admittance_detected ?a))
         )
 )

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; move above slot
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action move_above
 :parameters (?a - arm ?s - slot ?d - slot)
 :precondition (and (arm_above ?a ?s)
                 (arm_canreach ?a ?d)
                 (slot_free ?d)
                 ; (collision_free ?a)
                 ; (admittance_free ?a)
                 )
 :effect (and (not (arm_above ?a ?s))
              (slot_free ?s)
              (not (slot_free ?d))
              (arm_above ?a ?d)
              ; (stop_collision_avoidance ?a)
              ; (stop_admittance_avoidance ?a)
         )
 )

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; approach solenoid/slot
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action approach_to_grasp
 :parameters (?a - arm ?o - solenoid ?s - slot)
 :precondition (and (arm_above ?a ?s)
                 (object_in ?o ?s)
                 (arm_free ?a)
                 (collision_free ?a)
                 (admittance_free ?a)
                 )
 :effect (and (not (arm_above ?a ?s))
              (arm_at ?a ?s)
         )
)

(:action approach_to_insert
 :parameters (?a - arm ?o - solenoid ?s - slot)
 :precondition (and (arm_above ?a ?s)
                 (slot_empty ?s)
                 (arm_gripping ?a ?o)
                 (collision_free ?a)
                 (admittance_free ?a)
                 )
 :effect (and (not (arm_above ?a ?s))
              (arm_at ?a ?s)
         )
 )

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; lift gripped object in slot
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action lift
 :parameters (?a - arm ?o - solenoid ?s - slot)
 :precondition (and (arm_at ?a ?s)
                    (object_in ?o ?s)
                    (arm_gripping ?a ?o))
 :effect (and (not (arm_at ?a ?s))
              (arm_above ?a ?s)
              (not (object_in ?o ?s))
              (slot_empty ?s)
         )
)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; leave slot while arm is free
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action leave
 :parameters (?a - arm ?s - slot)
 :precondition (and (arm_at ?a ?s)
                    (arm_free ?a)
               )
 :effect (and (not (arm_at ?a ?s))
              (arm_above ?a ?s)
         )
)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; grip solenoid
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action grip
 :parameters (?a - arm ?o - solenoid ?s - slot)
 :precondition (and (arm_at ?a ?s)
                    (object_in ?o ?s)
                    (arm_free ?a)
               )
 :effect (and (not (arm_free ?a))
              (arm_gripping ?a ?o)
              (arm_gripping ?a ?o)
         )
)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; ungrip solenoid
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action ungrip
 :parameters (?a - arm ?o - solenoid ?s - slot)
 :precondition (and (arm_at ?a ?s)
                    (object_in ?o ?s)
                    (arm_gripping ?a ?o)
               )
 :effect (and (not (arm_gripping ?a ?o))
              (arm_free ?a)
         )
)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; insert and push solenoid
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action insert
 :parameters (?a - arm ?o - solenoid ?s - slot ?r - rack)
 :precondition (and (arm_gripping ?a ?o)
                    (has_slot ?r ?s)
                    (arm_at ?a ?s)
                    (slot_empty ?s)
               )
 :effect (and (not (slot_empty ?s))
              (object_in ?o ?s)
              (object_assembled ?o ?r)
         )
)

)

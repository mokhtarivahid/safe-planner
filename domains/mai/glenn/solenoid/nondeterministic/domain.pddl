(define (domain solenoid)
(:requirements :strips :typing :probabilistic-effects)
(:types solenoid hole)

(:predicates (on ?s - solenoid ?l - hole)
             (ontable ?s - solenoid)
             (robot_at ?h - hole)
             (human_at ?s - solenoid)
             (no_human_at ?s - solenoid)
             (holding ?s - solenoid)
             (removed ?s - solenoid ?l - hole)
             ; (request_state_update)
             (gripper_free)
             (robot_at_base)
             (robot_at_midway)
             ; (empty_hole)
             )

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; ABB actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; (:action update_state
;  :parameters   (?s - solenoid ?h - hole)
;  :precondition (and (request_state_update))
;  :effect       (and (when (on ?s ?h) (and (on ?s ?h)(not(request_state_update))))
;                     (when (not(on ?s ?h)) (empty_hole))
;                )
;  )

; (:action observe_human
;  :parameters   (?s - solenoid ?h - hole)
;  :precondition (and (on ?s ?h))
;  :effect       (and (no_human_at ?s))
;  )

(:action move_forward
 :parameters (?s - solenoid ?h - hole)
 :precondition (and (on ?s ?h)(robot_at_base))
 :effect (and
         (probabilistic 1/3 (and (no_human_at ?s)(robot_at ?h)(not(robot_at_base))))
         (probabilistic 1/3 (and (human_at ?s)(removed ?s ?h)(not(on ?s ?h))))
         (probabilistic 1/3 (and (human_at ?s)(removed ?s ?h)(not(on ?s ?h))(robot_at_midway)(not(robot_at_base))))))

(:action move_back
 :parameters ()
 :precondition (and (robot_at_midway))
 :effect (and (robot_at_base)(not(robot_at_midway))))

(:action pickup
 :parameters (?s - solenoid ?h - hole)
 :precondition (and (gripper_free)(robot_at ?h)(on ?s ?h))
 :effect (and (holding ?s)(removed ?s ?h)(not(gripper_free))(not(on ?s ?h))))

(:action carry_to_base
 :parameters (?s - solenoid ?h - hole)
 :precondition (and (holding ?s)(robot_at ?h))
 :effect (and (robot_at_base)(not(robot_at ?h))))

(:action putdown
 :parameters (?s - solenoid)
 :precondition (and (holding ?s)(robot_at_base))
 :effect (and (gripper_free)(ontable ?s)(not(holding ?s))))

)
(define (domain solenoid)
(:requirements :strips :typing :negative-preconditions :conditional-effects)
(:types solenoid hole)

(:predicates (on ?s - solenoid ?l - hole)
             (ontable ?s - solenoid)
             (robot_at ?s - solenoid)
             (human_at ?s - solenoid)
             (no_human_at ?s - solenoid)
             (holding ?s - solenoid)
             (removed ?s - solenoid ?l - hole)
             (request_state_update)
             (gripper_free)
             (robot_at_base)
             (empty_hole))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; ABB actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action update_state
 :parameters   (?s - solenoid ?h - hole)
 :precondition (and (request_state_update))
 :effect       (and (when (on ?s ?h) (and (on ?s ?h)(not(request_state_update))))
                    (when (not(on ?s ?h)) (empty_hole))
               )
 )

(:action observe_human
 :parameters   (?s - solenoid ?h - hole)
 :precondition (and (on ?s ?h))
 :effect       (and (no_human_at ?s))
 )

(:action move_forward
 :parameters (?s - solenoid ?h - hole)
 :precondition (and (on ?s ?h))
 :effect (when (and (robot_at_base)(no_human_at ?s)) (and (robot_at ?s)(not(robot_at_base)))))

(:action move_back
 :parameters (?s - solenoid ?h - hole)
 :precondition (and (on ?s ?h))
 :effect (when (and (human_at ?s) (not(robot_at_base)))
            (and(removed ?s ?h)(robot_at_base)(not(on ?s ?h)))))

; (:action move_to_base
;  :parameters ()
;  :precondition (not(robot_at_base))
;  :effect (robot_at_base))

(:action pickup
 :parameters (?s - solenoid ?h - hole)
 :precondition (and (gripper_free)(robot_at ?s)(on ?s ?h))
 :effect (and (holding ?s)(removed ?s ?h)(not(gripper_free))(not(robot_at ?s))(not(on ?s ?h))))

(:action carry_to_base
 :parameters (?s - solenoid)
 :precondition (holding ?s)
 :effect (and (robot_at_base)))

(:action putdown
 :parameters (?s - solenoid)
 :precondition (and (holding ?s)(robot_at_base))
 :effect (and (gripper_free)(ontable ?s)(not(holding ?s))))

)
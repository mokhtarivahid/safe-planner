(define (domain solenoid)
(:requirements :strips :typing :probabilistic-effects)
(:types solenoid hole)

(:predicates (on ?s - solenoid ?l - hole)
             (sensed_on ?s - solenoid ?l - hole)
             (ontable ?s - solenoid)
             (robot_at ?h - hole)
             (human_at ?s - solenoid)
             (no_human_at ?s - solenoid)
             (holding ?s - solenoid)
             (removed ?s - solenoid)
             (gripper_free)
             (robot_at_table)
             (sense_on)
             )

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; ABB actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action observe_solenoid
 :parameters   (?s - solenoid ?h - hole)
 :precondition (and (on ?s ?h)(sense_on))
 :effect (and
         (probabilistic 1/2 (and (sensed_on ?s ?h)(not(sense_on))))
         (probabilistic 1/2 (and (removed ?s)(not(on ?s ?h))))))

(:action move
 :parameters (?s - solenoid ?h - hole)
 :precondition (and (sensed_on ?s ?h)(robot_at_table))
 :effect (and
         (probabilistic 1/2 (and (no_human_at ?s)(robot_at ?h)(not(robot_at_table))))
         (probabilistic 1/2 (and (human_at ?s)(removed ?s)(not(sensed_on ?s ?h))(sense_on)))))

(:action pickup
  :parameters (?s - solenoid ?h - hole)
  :precondition (and (gripper_free)(robot_at ?h)(sensed_on ?s ?h))
  :effect (and (holding ?s)(removed ?s)(not(on ?s ?h))(not(sensed_on ?s ?h))(not(gripper_free))(sense_on)))

(:action carry
  :parameters (?s - solenoid ?h - hole)
  :precondition (and (holding ?s)(robot_at ?h))
  :effect (and (robot_at_table)(not(robot_at ?h))))

(:action putdown
  :parameters (?s - solenoid)
  :precondition (and (holding ?s)(robot_at_table))
  :effect (and (ontable ?s)(gripper_free)(not(holding ?s))))

)
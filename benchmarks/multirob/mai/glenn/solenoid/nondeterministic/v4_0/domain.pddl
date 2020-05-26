(define (domain solenoid)
(:requirements :strips :typing :negative-preconditions :probabilistic-effects)
(:types solenoid)

(:predicates 
             (ontable ?s - solenoid)
             (holding ?s - solenoid)
             (removed ?s - solenoid)
             (sense ?s - solenoid)
             (observe_state)
             (robot_at_table)
             (robot_at_home)
             (human_towards ?s - solenoid)
             (certainty_low ?s - solenoid)
             (certainty_high ?s - solenoid)
             (gripper_free))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; ABB actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action observe
 :parameters   (?s - solenoid)
 :precondition (and (sense ?s) (observe_state))
 :effect (and (when (and (human_towards ?s) (certainty_high ?s))
                    (and (not (human_towards ?s)) (not (certainty_high ?s))))
              (oneof (and (ontable ?s) (not (sense ?s)) (not (observe_state)))
                     (and (removed ?s) (not (sense ?s))))))

(:action move
 :parameters (?s - solenoid)
 :precondition (and (ontable ?s) (not (robot_at_table))
                    (forall (?x - solenoid) (and (not (human_towards ?s)) (not (certainty_low ?x)))))
 :effect (and (when (robot_at_home) (not (robot_at_home)))
              (oneof (robot_at_table)
                     (and (human_towards ?s) (certainty_low ?s))
                     (and (human_towards ?s) (certainty_high ?s) (sense ?s) (not (ontable ?s)) (observe_state)))))

(:action move_slow
 :parameters (?s - solenoid)
 :precondition (and (ontable ?s) (human_towards ?s) (certainty_low ?s) (not (robot_at_table)))
 :effect (and (when (robot_at_home) (not (robot_at_home)))
              (not (certainty_low ?s))
              (oneof (and (robot_at_table) (not (human_towards ?s))) 
                     (and (certainty_high ?s) (sense ?s) (not (ontable ?s)) (observe_state)))))

(:action grasp
  :parameters (?s - solenoid)
  :precondition (and (ontable ?s) (not (human_towards ?s)) (gripper_free) (robot_at_table))
  :effect (and (holding ?s) (not (ontable ?s)) (not (gripper_free))))

(:action move_home
  :parameters ()
  :precondition (not (robot_at_home))
  :effect (and (robot_at_home) (not (robot_at_table))))

(:action putdown
  :parameters (?s - solenoid)
  :precondition (and (holding ?s) (robot_at_home))
  :effect (and (removed ?s) (gripper_free) (not (holding ?s)) (observe_state)))

)
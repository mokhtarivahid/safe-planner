(define (domain solenoid)
(:requirements :strips :typing :negative-preconditions :probabilistic-effects)
(:types solenoid)

(:predicates (ontable ?s - solenoid)
             (holding ?s - solenoid)
             (removed ?s - solenoid)
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
 :precondition (and (ontable ?s) (human_towards ?s) (certainty_high ?s) (robot_at_home))
 :effect (and (not (human_towards ?s)) (not (certainty_high ?s))
              (probabilistic 0.5 (and (removed ?s) (not (ontable ?s))))))

(:action move
 :parameters (?s - solenoid)
 :precondition (and (ontable ?s) 
                    (forall (?x - solenoid) (and (not (human_towards ?s)) (not (certainty_low ?x)))))
 :effect (and (oneof (robot_at_table)
                     (and (human_towards ?s) (certainty_low ?s))
                     (and (human_towards ?s) (certainty_high ?s)))
              (not (robot_at_home))))

(:action move_slow
 :parameters (?s - solenoid)
 :precondition (and (ontable ?s) (human_towards ?s) (certainty_low ?s))
 :effect (and (oneof (certainty_high ?s)
                     (and (robot_at_table) (not (human_towards ?s))))
              (not (certainty_low ?s))))

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
  :effect (and (removed ?s) (gripper_free) (not (holding ?s))))

)
(define (domain solenoid)
(:requirements :strips :typing :negative-preconditions :probabilistic-effects)
(:types solenoid hole)

(:predicates (on ?s - solenoid ?l - hole)
             (sensed_on ?s - solenoid ?l - hole)
             (ontable ?s - solenoid)
             (robot_at ?h - hole)
             (human_at ?s - solenoid)
             (human_towards ?s - solenoid ?h - hole)
             (certainty_low ?s - solenoid)
             (certainty_high ?s - solenoid)
             (holding ?s - solenoid)
             (removed ?s - solenoid)
             (gripper_free)
             (robot_at_home)
             (state_observation_needed)
             )

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; ABB actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action observe_state
 :parameters   (?s - solenoid ?h - hole)
 :precondition (and (on ?s ?h)(state_observation_needed))
 :effect (and
         (oneof (and (sensed_on ?s ?h)(not(state_observation_needed)))
                (and (removed ?s)(not(on ?s ?h))))))

(:action move
 :parameters (?s - solenoid ?h - hole)
 :precondition (and (sensed_on ?s ?h)(robot_at_home)(not(human_towards ?s ?h)))
 :effect (and
         (oneof (and (robot_at ?h)(not(robot_at_home)))
                (and (human_towards ?s ?h)(certainty_low ?s))
                (and (human_towards ?s ?h)(certainty_high ?s))
                (and (removed ?s)(not(sensed_on ?s ?h))(state_observation_needed)))))

(:action move_slow
 :parameters (?s - solenoid ?h - hole)
 :precondition (and (sensed_on ?s ?h)(human_towards ?s ?h)(certainty_low ?s))
 :effect (and (not(certainty_low ?s))
         (oneof (and (robot_at ?h)(not(robot_at_home))(not(human_towards ?s ?h)))
                (and (not(human_towards ?s ?h)))
                (and (certainty_high ?s))
                (and (removed ?s)(not(sensed_on ?s ?h))(state_observation_needed)(not(human_towards ?s ?h))))))

(:action move_stop
 :parameters (?s - solenoid ?h - hole)
 :precondition (and (sensed_on ?s ?h)(human_towards ?s ?h)(certainty_high ?s))
 :effect (and (not(certainty_high ?s))
         (oneof (and (certainty_low ?s))
                (and (not(human_towards ?s ?h)))
                (and (removed ?s)(not(sensed_on ?s ?h))(state_observation_needed)(not(human_towards ?s ?h))))))

(:action grasp
  :parameters (?s - solenoid ?h - hole)
  :precondition (and (gripper_free)(robot_at ?h)(sensed_on ?s ?h))
  :effect (and (holding ?s)(removed ?s)(not(on ?s ?h))(not(sensed_on ?s ?h))(not(gripper_free))))

(:action carry
  :parameters (?s - solenoid ?h - hole)
  :precondition (and (holding ?s)(robot_at ?h))
  :effect (and (robot_at_home)(not(robot_at ?h))))

(:action putdown
  :parameters (?s - solenoid)
  :precondition (and (holding ?s)(robot_at_home))
  :effect (and (ontable ?s)(gripper_free)(not(holding ?s))(state_observation_needed)))

)
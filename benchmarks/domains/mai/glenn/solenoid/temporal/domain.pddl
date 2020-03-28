(define (domain solenoid)
(:requirements :strips :typing :negative-preconditions :conditional-effects :durative-actions)
(:types solenoid hole)

(:predicates (on ?s - solenoid ?l - hole)
             (ontable ?s - solenoid)
             (robot_at ?h - hole)
             (human_at ?s - solenoid)
             (no_human_at ?s - solenoid)
             (holding ?s - solenoid)
             (removed ?s - solenoid)
             (request_state_update)
             (request_observe)
             (gripper_free)
             (robot_at_base)
             (robot_not_at_base)
             (empty_hole))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; ABB actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:durative-action no_human_intention
 :parameters (?s - solenoid ?h - hole)
 :duration (= ?duration 0.1)
 :condition (and (at start (request_observe))
                 (over all (on ?s ?h)))
 :effect (and (at start (not (request_observe)))
              (at end (no_human_at ?s))))

(:durative-action human_intention
 :parameters (?s - solenoid ?h - hole)
 :duration (= ?duration 0.1)
 :condition (and (at start (request_observe))
                 (over all (on ?s ?h)))
 :effect (and (at start (not (request_observe)))
              (at end (not (on ?s ?h)))
              (at end (human_at ?s))
              (at end (removed ?s))))

(:durative-action move_forward_succeed
 :parameters (?s - solenoid ?h - hole)
 :duration (= ?duration 0.2)
 :condition (and (at start (on ?s ?h))
                 (at start (robot_at_base))
                 (at end (no_human_at ?s)))
 :effect (and (at start (request_observe))
              (at start (not (robot_at_base)))
              (at start (robot_not_at_base))
              (at end (robot_at ?h))))

(:durative-action move_forward_failed
 :parameters (?s - solenoid ?h - hole)
 :duration (= ?duration 0.2)
 :condition (and (at start (on ?s ?h))
                 (at start (robot_at_base))
                 (at end (human_at ?s)))
 :effect (and (at start (request_observe))
              (at start (not (robot_at_base)))
              (at end (robot_at_base))))

(:durative-action pickup
 :parameters (?s - solenoid ?h - hole)
 :duration (= ?duration 0.1)
 :condition (and (at start (on ?s ?h))
                 (at start (robot_at ?h)))
 :effect (and (at start (not (on ?s ?h)))
              (at end (removed ?s))))

)
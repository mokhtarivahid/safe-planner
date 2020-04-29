(define (domain packaging)
(:requirements :strips :typing :probabilistic-effects)
(:types arm location)
(:predicates (arm ?l - arm)
             (surface ?l - location)
             (space ?l - location)
             (camera ?l - location)
             (package ?l - location)
             (container ?l - location)
             (graspable ?l - location)
             (location_free ?l - location)
             (object_in ?o - location ?l - location)
             (gripped ?a - arm ?o - location)
             (unknown_orientation ?o - location)
             (upward ?o - location)
             (downward ?o - location)
             (camera_checked ?o - location)
             (arm_canreach ?a - arm ?l - location)
             (arm_at ?a - arm ?l - location)
             (arm_free ?a - arm)
             (packed ?t - location ?l - location)
             (unblocked ?o - location)
             (blocked ?o - location ?b - location)
             (improper_grasp ?a - arm ?o - location))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; ABB actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; nil actions: helpful in partial order planner, e.g., 'optic'
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; (:action do_nothing
;  :parameters   (?a - arm ?s - location)
;  :precondition (and (arm_free ?a)(arm_at ?a ?s)(arm_canreach ?a ?s))
;  :effect       (and (arm_at ?a ?s)(location_free ?s)(not(location_free ?s))(not(arm_at ?a ?s))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; move/carry actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action move
 :parameters   (?a - arm ?s ?d - location)
 :precondition (and (arm_free ?a)(arm_at ?a ?s)(arm_canreach ?a ?d)(location_free ?d))
 :effect       (and (arm_at ?a ?d)(location_free ?s)(not(location_free ?d))(not(arm_at ?a ?s))))

(:action move_to_grasp
 :parameters   (?a - arm ?o - location ?s ?d - location)
 :precondition (and (arm_free ?a)(arm_at ?a ?s)(arm_canreach ?a ?d)(object_in ?o ?d)(location_free ?o))
 :effect       (and (arm_at ?a ?o)(not(location_free ?o))(not(arm_at ?a ?s))))

(:action carry_to_camera
 :parameters   (?a - arm ?o - location ?s ?d - location)
 :precondition (and (gripped ?a ?o)(arm_at ?a ?s)(arm_canreach ?a ?d)(location_free ?d)(camera ?d))
 :effect       (and (arm_at ?a ?d)(location_free ?s)(not(arm_at ?a ?s))(not(location_free ?d))))

(:action carry_to_pack
 :parameters   (?a - arm ?o - location ?s ?d - location)
 :precondition (and (camera_checked ?o)(gripped ?a ?o)(arm_at ?a ?s)(arm_canreach ?a ?d)(location_free ?d)(package ?d))
 :effect       (and (arm_at ?a ?d)(location_free ?s)(not(location_free ?d))(not(arm_at ?a ?s))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; grasp actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action grasp
 :parameters   (?a - arm ?o - location ?l - location)
 :precondition (and (arm_free ?a)(arm_at ?a ?o)(graspable ?o)(object_in ?o ?l)(unblocked ?o))
 :effect       (and (gripped ?a ?o)(not(arm_free ?a))(not(object_in ?o ?l))(arm_at ?a ?l)(not(arm_at ?a ?o))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; put/place actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action put_in_pack
 :parameters   (?a - arm ?o - location ?l - location)
 :precondition (and (downward ?o)(camera_checked ?o)(gripped ?a ?o)(arm_at ?a ?l)(package ?l))
 :effect       (and (packed ?o ?l)(arm_free ?a)(not(gripped ?a ?o))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; camera actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action check_direction
 :parameters   (?a - arm ?o - location ?l - location)
 :precondition (and (gripped ?a ?o)(arm_at ?a ?l)(camera ?l)(unknown_orientation ?o))
 :effect       (and (camera_checked ?o)
                    (probabilistic 0.5 (and (downward ?o)(not (unknown_orientation ?o)))
                                   0.5 (and (upward ?o)(not (unknown_orientation ?o))))))

; (:action check_direction
;  :parameters   (?a - arm ?o - location ?l - location)
;  :precondition (and (gripped ?a ?o)(arm_at ?a ?l)(camera ?l))
;  :effect       (and (camera_checked ?o)(upward ?o)))

(:action rotate
 :parameters   (?a - arm ?o - location)
 :precondition (and (gripped ?a ?o)(camera_checked ?o)(upward ?o))
 :effect       (and (not(upward ?o))(downward ?o)))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; possible geometric constraints and recovery actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; ;; in case of grasping an object at an improper grasp pose
; ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; ;; remove 'free' later, since the table does not become busy by one arm
; (:action carry_to_table
;  :parameters   (?a - arm ?o - location ?s ?d - location)
;  :precondition (and (improper_grasp ?a ?o)(gripped ?a ?o)(arm_at ?a ?s)(arm_canreach ?a ?d)(location_free ?d)(surface ?d))
;  :effect       (and (arm_at ?a ?d)(location_free ?s)(not(arm_at ?a ?s))(not(location_free ?d))))

; (:action put_on_table
;  :parameters   (?a - arm ?o - location ?l - location)
;  :precondition (and (improper_grasp ?a ?o)(gripped ?a ?o)(arm_at ?a ?l)(surface ?l))
;  :effect       (and (arm_free ?a)(object_in ?o ?l)(location_free ?o)(not(gripped ?a ?o))(not(improper_grasp ?a ?o))))

; (:action handover
;  :parameters   (?a1 ?a2 - arm ?o - location ?l1 ?l2 - location)
;  :precondition (and (improper_grasp ?a1 ?o)(arm_free ?a2)(gripped ?a1 ?o)(arm_at ?a1 ?l1)(arm_at ?a2 ?l2)(space ?l1)(space ?l2))
;  :effect       (and (gripped ?a2 ?o)(arm_free ?a1)(not(arm_free ?a2))(not(gripped ?a1 ?o))(not(improper_grasp ?a1 ?o))))

; ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; ;; in case of obstructing an object by another object
; ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; (:action object_cleared
;  :parameters   (?a - arm ?o - location ?b - location)
;  :precondition (and (gripped ?a ?b)(blocked ?o ?b))
;  :effect       (and (not(blocked ?o ?b))(unblocked ?o)))

)

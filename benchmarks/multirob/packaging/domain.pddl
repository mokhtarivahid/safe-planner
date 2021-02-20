(define (domain packaging)
(:requirements :strips :typing :probabilistic-effects)
; (:types location arm - object
;         graspable container camera assembly - location
;         cap base - graspable)
(:types arm graspable)
(:predicates (camera ?l - graspable)
             (package ?l - graspable)
             (free ?l - graspable)
             (object_in ?o - graspable ?l - graspable)
             (gripped ?a - arm ?o - graspable)
             (ungripped ?o - graspable)
             (unknown_orientation ?o - graspable)
             (upward ?o - graspable)
             (downward ?o - graspable)
             (camera_checked ?o - graspable)
             (arm_canreach ?a - arm ?l - graspable)
             (arm_at ?a - arm ?l - graspable)
             (arm_free ?a - arm)
             (packed ?g - graspable ?l - graspable))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; ABB actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; move/carry actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action move_to_grasp
 :parameters   (?a - arm ?o - graspable ?s ?d - graspable)
 :precondition (and (arm_free ?a)(arm_at ?a ?s)(arm_canreach ?a ?d)(object_in ?o ?d)(free ?o))
 :effect       (and (arm_at ?a ?o)(free ?s)(not(free ?o))(not(arm_at ?a ?s))))

(:action carry_to_camera
 :parameters   (?a - arm ?o - graspable ?s ?d - graspable)
 :precondition (and (gripped ?a ?o)(arm_at ?a ?s)(arm_canreach ?a ?d)(free ?d)(camera ?d))
 :effect       (and (arm_at ?a ?d)(free ?s)(not(arm_at ?a ?s))(not(free ?d))))

;; carry while grasping an graspable
(:action carry_to_pack
 :parameters   (?a - arm ?o - graspable ?s ?d - graspable)
 :precondition (and (gripped ?a ?o)(arm_at ?a ?s)(arm_canreach ?a ?d)(package ?d))
 :effect       (and (arm_at ?a ?d)(free ?s)(not(arm_at ?a ?s))(not(free ?d))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; vacuum/grip actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action grasp
 :parameters   (?a - arm ?o - graspable ?l - graspable)
 :precondition (and (arm_free ?a)(arm_at ?a ?o)(object_in ?o ?l))
 :effect       (and (gripped ?a ?o)(not(arm_free ?a))(not(object_in ?o ?l))(arm_at ?a ?l)(not(arm_at ?a ?o))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; put/place actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action put_in_pack
 :parameters   (?a - arm ?o - graspable ?l - graspable)
 :precondition (and (gripped ?a ?o)(upward ?o)(arm_at ?a ?l)(package ?l))
 :effect       (and (packed ?o ?l)(arm_free ?a)(not(gripped ?a ?o))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; camera actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action check_orientation
 :parameters   (?a - arm ?o - graspable ?l - graspable)
 :precondition (and (gripped ?a ?o)(arm_at ?a ?l)(camera ?l)(unknown_orientation ?o))
 :effect       (and (camera_checked ?o)
                    (probabilistic 0.5 (and (downward ?o)(not (unknown_orientation ?o)))
                                   0.5 (and (upward ?o)(not (unknown_orientation ?o))))))

(:action rotate
 :parameters   (?a - arm ?o - graspable)
 :precondition (and (gripped ?a ?o)(camera_checked ?o)(downward ?o))
 :effect       (and (not(downward ?o))(upward ?o)))

; (:action rotate
;  :parameters   (?a - arm ?o - graspable)
;  :precondition (and (gripped ?a ?o)(camera_checked ?o))
;  :effect       (and (when (upward ?o) (downward ?o))
;                     (when (downward ?o) (upward ?o))))

)

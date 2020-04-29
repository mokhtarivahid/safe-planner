(define (domain packaging)
(:requirements :strips :typing :probabilistic-effects)
; (:types location arm - object
;         graspable container camera assembly - location
;         cap base - graspable)
(:types arm object)
(:predicates (camera ?l - object)
             (package ?l - object)
             (peg ?l - object)
             (hole ?l - object)
             (assembly ?l - object)
             (free ?l - object)
             (base ?o - object)
             (cap ?o - object)
             (object_in ?o - object ?l - object)
             (vacuumed ?a - arm ?o - object)
             (gripped ?a - arm ?o - object)
             (ungripped ?o - object)
             (unknown_orientation ?o - object)
             (upward ?o - object)
             (downward ?o - object)
             (camera_checked ?o - object)
             (arm_canreach ?a - arm ?l - object)
             (arm_at ?a - arm ?l - object)
             (arm_free ?a - arm)
             (assembled ?t - object ?b - object)
             (packed ?t - object ?b - object ?l - object))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; ABB actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; move/carry actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action move_to_grasp
 :parameters   (?a - arm ?o - object ?s ?d - object)
 :precondition (and (arm_free ?a)(arm_at ?a ?s)(arm_canreach ?a ?d)(object_in ?o ?d)(free ?o))
 :effect       (and (arm_at ?a ?o)(free ?s)(not(free ?o))(not(arm_at ?a ?s))))

;; carry while vacuuming an object
; (:action carry
;  :parameters   (?a - arm ?o - object ?s ?d - object)
;  :precondition (and (vacuumed ?a ?o)(arm_at ?a ?s)(arm_canreach ?a ?d)(free ?d))
;  :effect       (and (arm_at ?a ?d)(free ?s)(not(arm_at ?a ?s))(not(free ?d))))

(:action carry_to_camera
 :parameters   (?a - arm ?o - object ?s ?d - object)
 :precondition (and (vacuumed ?a ?o)(arm_at ?a ?s)(arm_canreach ?a ?d)(free ?d)(camera ?d))
 :effect       (and (arm_at ?a ?d)(free ?s)(not(arm_at ?a ?s))(not(free ?d))))

(:action carry_to_peg
 :parameters   (?a - arm ?o - object ?s ?d - object)
 :precondition (and (vacuumed ?a ?o)(arm_at ?a ?s)(arm_canreach ?a ?d)(free ?d)(peg ?d))
 :effect       (and (arm_at ?a ?d)(free ?s)(not(arm_at ?a ?s))(not(free ?d))))

(:action carry_to_hole
 :parameters   (?a - arm ?o - object ?s ?d - object)
 :precondition (and (vacuumed ?a ?o)(arm_at ?a ?s)(arm_canreach ?a ?d)(free ?d)(hole ?d))
 :effect       (and (arm_at ?a ?d)(free ?s)(not(arm_at ?a ?s))(not(free ?d))))

; ;; carry while grasping an object
; (:action carry
;  :parameters   (?a - arm ?o - object ?s ?d - object)
;  :precondition (and (gripped ?a ?o)(arm_at ?a ?s)(arm_canreach ?a ?d)(free ?d))
;  :effect       (and (arm_at ?a ?d)(free ?s)(not(arm_at ?a ?s))(not(free ?d))))

;; carry while grasping an object
(:action carry_to_assemble
 :parameters   (?a - arm ?o - object ?s ?d - object)
 :precondition (and (gripped ?a ?o)(arm_at ?a ?s)(arm_canreach ?a ?d)(free ?d)(assembly ?d))
 :effect       (and (arm_at ?a ?d)(free ?s)(not(arm_at ?a ?s))(not(free ?d))))

(:action carry_to_pack
 :parameters   (?a - arm ?o1 ?o2 - object ?s ?d - object)
 :precondition (and (assembled ?o1 ?o2)(gripped ?a ?o1)(arm_at ?a ?s)(arm_canreach ?a ?d)(free ?d)(ungripped ?o2)(package ?d))
 :effect       (and (arm_at ?a ?d)(free ?s)(not(free ?d))(not(arm_at ?a ?s))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; vacuum/grip actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action vacuum
 :parameters   (?a - arm ?o - object ?l - object)
 :precondition (and (arm_free ?a)(arm_at ?a ?o)(object_in ?o ?l))
 :effect       (and (vacuumed ?a ?o)(not(arm_free ?a))(not(object_in ?o ?l))(arm_at ?a ?l)(not(arm_at ?a ?o))))

(:action grasp
 :parameters   (?a - arm ?o - object ?l - object)
 :precondition (and (arm_free ?a)(arm_at ?a ?o)(object_in ?o ?l))
 :effect       (and (gripped ?a ?o)(not(arm_free ?a))(not(object_in ?o ?l))(arm_at ?a ?l)(not(arm_at ?a ?o))))

(:action ungrip
 :parameters   (?a - arm ?o1 ?o2 - object ?l - object)
 :precondition (and (assembled ?o1 ?o2)(gripped ?a ?o2)(base ?o2)(arm_at ?a ?l))
 :effect       (and (free ?l)(arm_free ?a)(ungripped ?o2)(not(gripped ?a ?o2))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; put/place actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action put_in_peg
 :parameters   (?a - arm ?o - object ?l - object)
 :precondition (and (vacuumed ?a ?o)(arm_at ?a ?l)(downward ?o)(base ?o)(peg ?l))
 :effect       (and (arm_free ?a)(object_in ?o ?l)(free ?o)(not(vacuumed ?a ?o))(not(downward ?o))))

(:action put_in_hole
 :parameters   (?a - arm ?o - object ?l - object)
 :precondition (and (vacuumed ?a ?o)(arm_at ?a ?l)(downward ?o)(cap ?o)(hole ?l))
 :effect       (and (arm_free ?a)(object_in ?o ?l)(free ?o)(not(vacuumed ?a ?o))(not(downward ?o))))

(:action put_in_pack
 :parameters   (?a - arm ?o1 ?o2 - object ?l - object)
 :precondition (and (assembled ?o1 ?o2)(gripped ?a ?o1)(arm_at ?a ?l)(package ?l))
 :effect       (and (packed ?o1 ?o2 ?l)(arm_free ?a)(not(gripped ?a ?o1))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; camera actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action check_direction
 :parameters   (?a - arm ?o - object ?l - object)
 :precondition (and (vacuumed ?a ?o)(arm_at ?a ?l)(camera ?l)(unknown_orientation ?o))
 :effect       (and (camera_checked ?o)
                    (probabilistic 0.5 (and (downward ?o)(not (unknown_orientation ?o)))
                                   0.5 (and (upward ?o)(not (unknown_orientation ?o))))))

; (:action check_direction
;  :parameters   (?a - arm ?o - object ?l - object)
;  :precondition (and (vacuumed ?a ?o)(arm_at ?a ?l)(camera ?l))
;  :effect       (and (camera_checked ?o)(upward ?o)))

(:action rotate
 :parameters   (?a - arm ?o - object)
 :precondition (and (vacuumed ?a ?o)(camera_checked ?o)(upward ?o))
 :effect       (and (not(upward ?o))(downward ?o)))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; assemble actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action assemble
 :parameters   (?a1 ?a2 - arm ?o1 ?o2 - object ?l1 ?l2 - object)
 :precondition (and (gripped ?a1 ?o1)(arm_at ?a1 ?l1)(assembly ?l1)
                    (gripped ?a2 ?o2)(arm_at ?a2 ?l2)(assembly ?l2)
                    (cap ?o1)(base ?o2)
                    (camera_checked ?o1)(camera_checked ?o2))
 :effect       (and (assembled ?o1 ?o2)(not(camera_checked ?o1))(not(camera_checked ?o2))))
)

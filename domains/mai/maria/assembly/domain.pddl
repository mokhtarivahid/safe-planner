(define (domain packaging)
(:requirements :strips :typing)
; (:types location arm - object
;         graspable container camera assembly - location
;         cap base - graspable)
(:types arm graspable)
(:predicates (package ?l - graspable)
             (peg ?l - graspable)
             (hole ?l - graspable)
             (assembly ?l - graspable)
             (free ?l - graspable)
             (base ?o - graspable)
             (cap ?o - graspable)
             (object_in ?o - graspable ?l - graspable)
             (gripped ?a - arm ?o - graspable)
             (ungripped ?o - graspable)
             (arm_canreach ?a - arm ?l - graspable)
             (arm_at ?a - arm ?l - graspable)
             (arm_free ?a - arm)
             (assembled ?t - graspable ?b - graspable)
             (packed ?t - graspable ?b - graspable ?l - graspable))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; ABB actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action move_to_grasp
 :parameters   (?a - arm ?o - graspable ?s ?d - graspable)
 :precondition (and (arm_free ?a)(arm_at ?a ?s)(arm_canreach ?a ?d)(object_in ?o ?d)(free ?o))
 :effect       (and (arm_at ?a ?o)(free ?s)(not(free ?o))(not(arm_at ?a ?s))))

(:action grasp
 :parameters   (?a - arm ?o - graspable ?l - graspable)
 :precondition (and (arm_free ?a)(arm_at ?a ?o)(object_in ?o ?l))
 :effect       (and (gripped ?a ?o)(not(arm_free ?a))(not(object_in ?o ?l))(arm_at ?a ?l)(not(arm_at ?a ?o))))

(:action ungrip
 :parameters   (?a - arm ?o1 ?o2 - graspable ?l - graspable)
 :precondition (and (assembled ?o1 ?o2)(gripped ?a ?o2)(base ?o2)(arm_at ?a ?l))
 :effect       (and (free ?l)(arm_free ?a)(ungripped ?o2)(not(gripped ?a ?o2))))

(:action carry_to_assemble
 :parameters   (?a - arm ?o - graspable ?s ?d - graspable)
 :precondition (and (gripped ?a ?o)(arm_at ?a ?s)(arm_canreach ?a ?d)(free ?d)(assembly ?d))
 :effect       (and (arm_at ?a ?d)(free ?s)(not(arm_at ?a ?s))(not(free ?d))))

(:action carry_to_pack
 :parameters   (?a - arm ?o1 ?o2 - graspable ?s ?d - graspable)
 :precondition (and (assembled ?o1 ?o2)(gripped ?a ?o1)(arm_at ?a ?s)(arm_canreach ?a ?d)(free ?d)(ungripped ?o2)(package ?d))
 :effect       (and (arm_at ?a ?d)(free ?s)(not(free ?d))(not(arm_at ?a ?s))))

(:action put_in_package
 :parameters   (?a - arm ?o1 ?o2 - graspable ?l - graspable)
 :precondition (and (assembled ?o1 ?o2)(gripped ?a ?o1)(arm_at ?a ?l)(package ?l))
 :effect       (and (packed ?o1 ?o2 ?l)(arm_free ?a)(not(gripped ?a ?o1))))

(:action assemble
 :parameters   (?a1 ?a2 - arm ?o1 ?o2 - graspable ?l1 ?l2 - graspable)
 :precondition (and (gripped ?a1 ?o1)(arm_at ?a1 ?l1)(assembly ?l1)
                    (gripped ?a2 ?o2)(arm_at ?a2 ?l2)(assembly ?l2)
                    (cap ?o1)(base ?o2))
 :effect       (and (assembled ?o1 ?o2)))
)

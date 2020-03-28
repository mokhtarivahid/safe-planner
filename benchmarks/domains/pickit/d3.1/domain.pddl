(define (domain packaging)
(:requirements :strips :typing :probabilistic-effects)
(:types graspable container camera assembly location arm)
(:predicates (camera ?l - location)
             (package ?l - location)
             (peg ?l - location)
             (hole ?l - location)
             (assembly ?l - location)
             (free ?l - location)
             (base ?o - location)
             (cap ?o - location)
             (object_in ?o - location ?l - location)
             (vacuumed ?a - arm ?o - location)
             (gripped ?a - arm ?o - location)
             (ungripped ?o - location)
             (upward ?o - location)
             (downward ?o - location)
             (unknown_pos ?o - location)
             (camera_checked ?o - location)
             (arm_canreach ?a - arm ?l - location)
             (arm_at ?a - arm ?l - location)
             (arm_free ?a - arm)
             (assembled ?t - location ?b - location)
             (packed ?t - location ?b - location ?l - location))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; move/carry actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action move_to_grasp
 :parameters   (?a - arm ?o - location ?s ?d - location)
 :precondition (and (arm_free ?a)(arm_at ?a ?s)(arm_canreach ?a ?d)
                    (object_in ?o ?d)(free ?o))
 :effect       (and (arm_at ?a ?o)(free ?s)(not(free ?o))(not(arm_at ?a ?s))))

(:action carry_to_camera
 :parameters   (?a - arm ?o - location ?s ?d - location)
 :precondition (and (vacuumed ?a ?o)(arm_at ?a ?s)(arm_canreach ?a ?d)
                    (free ?d)(camera ?d))
 :effect       (and (arm_at ?a ?d)(free ?s)(not(arm_at ?a ?s))(not(free ?d))))

(:action carry_to_peg
 :parameters   (?a - arm ?o - location ?s ?d - location)
 :precondition (and (vacuumed ?a ?o)(arm_at ?a ?s)(arm_canreach ?a ?d)
                    (free ?d)(peg ?d))
 :effect       (and (arm_at ?a ?d)(free ?s)(not(arm_at ?a ?s))(not(free ?d))))

(:action carry_to_hole
 :parameters   (?a - arm ?o - location ?s ?d - location)
 :precondition (and (vacuumed ?a ?o)(arm_at ?a ?s)(arm_canreach ?a ?d)
                    (free ?d)(hole ?d))
 :effect       (and (arm_at ?a ?d)(free ?s)(not(arm_at ?a ?s))(not(free ?d))))

(:action carry_to_assemble
 :parameters   (?a - arm ?o - location ?s ?d - location)
 :precondition (and (gripped ?a ?o)(arm_at ?a ?s)(arm_canreach ?a ?d)
                    (free ?d)(assembly ?d))
 :effect       (and (arm_at ?a ?d)(free ?s)(not(arm_at ?a ?s))(not(free ?d))))

(:action carry_to_pack
 :parameters   (?a - arm ?o1 ?o2 - location ?s ?d - location)
 :precondition (and (assembled ?o1 ?o2)(gripped ?a ?o1)(arm_at ?a ?s)
                    (arm_canreach ?a ?d)(free ?d)(ungripped ?o2)(package ?d))
 :effect       (and (arm_at ?a ?d)(free ?s)(not(free ?d))(not(arm_at ?a ?s))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; vacuum/grip/ungrip actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action vacuum
 :parameters   (?a - arm ?o - location ?l - location)
 :precondition (and (arm_free ?a)(arm_at ?a ?o)(object_in ?o ?l))
 :effect       (and (vacuumed ?a ?o)(not(arm_free ?a))(not(object_in ?o ?l))
                    (arm_at ?a ?l)(not(arm_at ?a ?o))))

(:action grip
 :parameters   (?a - arm ?o - location ?l - location)
 :precondition (and (arm_free ?a)(arm_at ?a ?o)(object_in ?o ?l))
 :effect       (and (gripped ?a ?o)(not(arm_free ?a))(not(object_in ?o ?l))
                    (arm_at ?a ?l)(not(arm_at ?a ?o))))

(:action ungrip
 :parameters   (?a - arm ?o1 ?o2 - location ?l - location)
 :precondition (and (assembled ?o1 ?o2)(gripped ?a ?o2)(base ?o2)(arm_at ?a ?l))
 :effect       (and (arm_free ?a)(free ?l)(ungripped ?o2)(not(gripped ?a ?o2))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; put/place actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action put_in_peg
 :parameters   (?a - arm ?o - location ?l - location)
 :precondition (and (vacuumed ?a ?o)(arm_at ?a ?l)(downward ?o)(base ?o)(peg ?l))
 :effect       (and (arm_free ?a)(object_in ?o ?l)(free ?o)
                    (not(vacuumed ?a ?o))(not(downward ?o))))

(:action put_in_hole
 :parameters   (?a - arm ?o - location ?l - location)
 :precondition (and (vacuumed ?a ?o)(arm_at ?a ?l)(downward ?o)(cap ?o)(hole ?l))
 :effect       (and (arm_free ?a)(object_in ?o ?l)(free ?o)
                    (not(vacuumed ?a ?o))(not(downward ?o))))

(:action put_in_pack
 :parameters   (?a - arm ?o1 ?o2 - location ?l - location)
 :precondition (and (assembled ?o1 ?o2)(gripped ?a ?o1)(arm_at ?a ?l)(package ?l))
 :effect       (and (packed ?o1 ?o2 ?l)(arm_free ?a)(not(gripped ?a ?o1))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; camera actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action check_orientation
 :parameters   (?a - arm ?o - location ?l - location)
 :precondition (and (vacuumed ?a ?o)(unknown_pos ?o)(arm_at ?a ?l)(camera ?l))
 :effect       (and (camera_checked ?o)
                    (oneof (and (downward ?o)(not(unknown_pos ?o)))
                           (and (upward ?o)(not(unknown_pos ?o))))))

(:action rotate
 :parameters   (?a - arm ?o - location)
 :precondition (and (vacuumed ?a ?o)(camera_checked ?o)(upward ?o))
 :effect       (and (not(upward ?o))(downward ?o)))

(:action rotate
 :parameters   (?a - arm ?o - location)
 :precondition (and (vacuumed ?a ?o)(camera_checked ?o)(downward ?o))
 :effect       (and (not(downward ?o))(upward ?o)))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; assemble actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action assemble
 :parameters   (?a1 ?a2 - arm ?o1 ?o2 - location ?l1 ?l2 - location)
 :precondition (and (gripped ?a1 ?o1)(arm_at ?a1 ?l1)(assembly ?l1)
                    (gripped ?a2 ?o2)(arm_at ?a2 ?l2)(assembly ?l2)
                    (cap ?o1)(base ?o2)
                    (camera_checked ?o1)(camera_checked ?o2))
 :effect       (and (assembled ?o1 ?o2)(not(camera_checked ?o1))
                    (not(camera_checked ?o2))))
)
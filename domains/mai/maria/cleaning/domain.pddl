(define (domain packaging)
(:requirements :strips :typing)
(:types location arm - object
        graspable container table - location)
(:predicates (location_free ?l - location)
             (on ?o - graspable ?l - location)
             (in ?o - graspable ?l - location)
             (arm_holding ?a - arm ?o - graspable)
             (arm_canreach ?a - arm ?l - location)
             (arm_at ?a - arm ?l - location)
             (arm_free ?a - arm))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; ABB actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action move_to_grasp
 :parameters   (?a - arm ?o - graspable ?s ?d - location)
 :precondition (and (arm_free ?a)(arm_at ?a ?s)(arm_canreach ?a ?d)
                    (on ?o ?d)(location_free ?o))
 :effect       (and (arm_at ?a ?o)(location_free ?s)(not(location_free ?o))(not(arm_at ?a ?s))))

(:action grasp
 :parameters   (?a - arm ?o - graspable ?l - location)
 :precondition (and (arm_free ?a)(arm_at ?a ?o)(on ?o ?l))
 :effect       (and (arm_holding ?a ?o)(not(arm_free ?a))(not(on ?o ?l))
                    (arm_at ?a ?l)(not(arm_at ?a ?o))))

(:action carry_to_crate
 :parameters   (?a - arm ?o - graspable ?s ?d - location)
 :precondition (and (arm_holding ?a ?o)(arm_at ?a ?s)(arm_canreach ?a ?d))
 :effect       (and (arm_at ?a ?d)(location_free ?s)(not(arm_at ?a ?s))))

(:action put_in_crate
 :parameters   (?a - arm ?o - graspable ?l - location)
 :precondition (and (arm_holding ?a ?o)(arm_at ?a ?l))
 :effect       (and (arm_free ?a)(in ?o ?l)(location_free ?o)(not(arm_holding ?a ?o))))

)
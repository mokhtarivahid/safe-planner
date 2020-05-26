(define (domain robotic-arms)

  (:requirements :strips :typing :probabilistic-effects)

  (:types robot table crate object)

  (:predicates  
                (arm ?o - robot)
                (crate ?c - crate)
                (table ?t - table)

                (arm_canput ?a - robot ?o - crate)
                (arm_canreach ?a - robot ?o - object)
                (arm_holding ?a - robot ?o - object)
                (arm_free ?a - robot)
 
                (on ?o - object ?t - table)
                (in ?o - object ?c - crate)

                (clear ?o - object)
                (blocked ?o - object ?b - object)
                )

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; (:action grasp_from_table
;  :parameters   (?a - robot ?o - object ?t - table)
;  :precondition (and (arm_free ?a) (arm_canreach ?a ?o) (on ?o ?t) (clear ?o))
;  :effect       (and (arm_holding ?a ?o) (not (arm_free ?a)) (not (on ?o ?t))))

(:action grasp_from_table
 :parameters   (?a - robot ?o - object ?t - table)
 :precondition (and (arm_free ?a) (arm_canreach ?a ?o) (on ?o ?t) (clear ?o))
 :effect       (and (probabilistic 0.5 (and (arm_holding ?a ?o) (not (arm_free ?a)) (not (on ?o ?t))))
                    (probabilistic 0.5 (and (arm_free ?a) (arm_canreach ?a ?o) (on ?o ?t) (clear ?o)))))

(:action grasp_from_crate
 :parameters   (?a - robot ?o - object ?c - crate)
 :precondition (and (arm_free ?a) (arm_canreach ?a ?o) (arm_canput ?a ?c) (in ?o ?c) (crate ?c) (clear ?o))
 :effect       (and (arm_holding ?a ?o) (not (arm_free ?a)) (not (in ?o ?c))))

(:action place_on_table
 :parameters   (?a - robot ?o - object ?t - table)
 :precondition (and (table ?t) (arm_holding ?a ?o))
 :effect       (and (arm_free ?a) (arm_canreach ?a ?o) (on ?o ?t) (not (arm_holding ?a ?o))))

(:action put_in_crate
 :parameters   (?a - robot ?o - object ?c - crate)
 :precondition (and (crate ?c) (arm_holding ?a ?o) (arm_canput ?a ?c))
 :effect       (and (arm_free ?a) (arm_canreach ?a ?o) (in ?o ?c) (not (arm_holding ?a ?o))))

(:action handover
 :parameters   (?s - robot ?o - object ?d - robot)
 :precondition (and (arm_holding ?s ?o) (arm_free ?d))
 :effect       (and (arm_free ?s) (not (arm_free ?d)) (arm_holding ?d ?o) (not (arm_holding ?s ?o))))

(:action object_cleared
 :parameters   (?a - robot ?o - object ?b - object)
 :precondition (and (arm_holding ?a ?b) (blocked ?o ?b))
 :effect       (and (not (blocked ?o ?b)) (clear ?o)))

)
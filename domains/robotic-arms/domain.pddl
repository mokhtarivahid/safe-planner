(define (domain robotic-arms)

  (:requirements :strips :typing)

  (:types robot table object)

  (:predicates  
                (arm ?o - robot)
                (crate ?c - object)
                (table ?t - table)

                (arm_canreach ?a - robot ?o - object)
                (arm_holding ?a - robot ?o - object)
                (arm_free ?a - robot)
 
                (on ?o - object ?t - table)
                (in ?o - object ?c - object)
                )

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action grasp_from_table
 :parameters   (?a - robot ?o - object ?t - table)
 :precondition (and (arm_free ?a) (arm_canreach ?a ?o) (on ?o ?t))
 :effect       (and (arm_holding ?a ?o) (not (arm_free ?a)) (not (on ?o ?t))))

(:action grasp_from_crate
 :parameters   (?a - robot ?o - object ?c - object)
 :precondition (and (arm_free ?a) (arm_canreach ?a ?o) (in ?o ?c) (crate ?c))
 :effect       (and (arm_holding ?a ?o) (not (arm_free ?a)) (not (in ?o ?c))))

(:action put_on_table
 :parameters   (?a - robot ?o - object ?t - table)
 :precondition (and (table ?t) (arm_holding ?a ?o))
 :effect       (and (arm_free ?a) (arm_canreach ?a ?o) (on ?o ?t) (not (arm_holding ?a ?o))))

(:action put_in_crate
 :parameters   (?a - robot ?o - object ?c - object)
 :precondition (and (crate ?c) (arm_holding ?a ?o))
 :effect       (and (arm_free ?a) (arm_canreach ?a ?o) (in ?o ?c) (not (arm_holding ?a ?o))))

)
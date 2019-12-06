(define (domain hie)
(:requirements :strips :typing :conditional-effects)
(:types hole arm object)

(:predicates (location_free ?l - hole)
             (at ?o - object ?l - hole)
             (arm_at_base ?a - arm)
             (arm_at ?a - arm ?l - hole)
             (arm_free ?a - arm))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; ABB actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action move_to_grasp
 :parameters   (?a - arm ?o - object ?h - hole)
 :precondition (and (arm_free ?a)(arm_at_base ?a)(at ?o ?h)(location_free ?h))
 :effect       (and (when (at ?o ?h) (and (arm_at ?a ?h)(not(location_free ?h))(not(arm_at_base ?a))))
                    (when (not(at ?o ?h)) (arm_at_base ?a))
               )
 )

)
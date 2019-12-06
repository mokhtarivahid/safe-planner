(define (domain tabletop)

  (:requirements :strips :typing :equality :negative-preconditions :existential-preconditions :universal-preconditions)

  (:types arm object)

  (:predicates  (free ?a - arm)
                (holding ?o - object)
                (reachable ?a - arm ?g - object)
                (unobstructed ?o ?b - object)
                )

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; pick up actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action pickup
 :parameters   (?a - arm ?o - object)
 :precondition (and (free ?a)(reachable ?a ?o)
                    (forall (?b - object) (and (not(= ?b ?o))(unobstructed ?o ?b))))
 :effect       (and (not(free ?a))(holding ?o)))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; actions to delete constraints in a state upon happening some other actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; (:action unobstructed
;  :parameters   (?g - grasp_pose ?o - object)
;  :precondition (and (obstructed ?g ?o)(lifted ?o))
;  :effect       (and (not(obstructed ?g ?o))(unobstructed ?g)))

; (:action unobstructed
;  :parameters   (?g - grasp_pose ?o - object)
;  :precondition (and (obstructed ?g ?o)(co_lifted ?o))
;  :effect       (and (not(obstructed ?g ?o))(unobstructed ?g)))

)
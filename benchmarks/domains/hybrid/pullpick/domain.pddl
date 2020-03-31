(define (domain pullandpick)

  (:requirements :strips :typing :negative-preconditions :conditional-effects :probabilistic-effects)
 
  (:types arm graspable - object)

  (:predicates  (free ?a - arm)

                (reachable ?a - arm ?o - graspable)

                (ontable ?o - graspable)
                (lifted ?o - graspable)

                (grasped ?a - arm ?o - graspable)
                (ungrasped ?o - graspable)

                (heavy ?o - graspable ?a - arm)
                (nearby ?o - graspable ?a - arm)

                (unobstructed ?o - graspable)

                ; ?o is obstructed by ?b to pull off
                (obstructed ?o - graspable ?b - object) 
                )

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; grasp actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action grasp
 :parameters   (?a - arm ?o - graspable)
 :precondition (and (free ?a)(ontable ?o)(reachable ?a ?o)(ungrasped ?o)(unobstructed ?o))
 :effect       (and (grasped ?a ?o)(not(ungrasped ?o))(not(free ?a))))

(:action ungrasp
 :parameters   (?a - arm ?o - graspable)
 :precondition (and (grasped ?a ?o)(ontable ?o))
 :effect       (and (free ?a)(ungrasped ?o)(not(grasped ?a ?o))
                    (forall (?x - graspable)
                        (when (obstructed ?x ?a) 
                            (and (unobstructed ?x)(not(obstructed ?x ?a)))))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; pick up actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action pickup
 :parameters   (?a - arm ?o - graspable)
 :precondition (and (grasped ?a ?o)(ontable ?o)(nearby ?o ?a)(not(heavy ?o ?a)))
 :effect       (and (oneof (and (lifted ?o)(not(ontable ?o))
                                (forall (?x - graspable)
                                    (when (obstructed ?x ?o) 
                                        (and (unobstructed ?x)(not(obstructed ?x ?o))))))
                           (and (heavy ?o ?a)(not (nearby ?o ?a))))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; pick up actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action pull
 :parameters   (?a - arm ?o - graspable)
 :precondition (and (grasped ?a ?o)(ontable ?o)(heavy ?o ?a)(unobstructed ?o))
 :effect       (and (nearby ?o ?a)(not(heavy ?o ?a))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; put down actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action put-on-table
 :parameters   (?a - arm ?o - graspable)
 :precondition (and (grasped ?a ?o)(lifted ?o))
 :effect       (and (ontable ?o)(ungrasped ?o)(free ?a)(not(grasped ?a ?o))(not(lifted ?o))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; actions to delete constraints in a state upon happening some other actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; (:action unobstruct
;  :parameters   (?b - graspable ?o - graspable)
;  :precondition (and (obstructed ?o ?b)(lifted ?b))
;  :effect       (and (not(obstructed ?o ?b))(unobstructed ?o)))

; (:action release
;  :parameters   (?a - arm ?o - graspable)
;  :precondition (and (obstructed ?o ?a)(free ?a))
;  :effect       (and (not(obstructed ?o ?a))(unobstructed ?o)))

)
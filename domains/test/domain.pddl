(define (domain tabletop)

  (:requirements :strips :typing :equality :negative-preconditions :existential-preconditions :universal-preconditions)

  (:types arm table tray object grasp_pose)

  (:predicates  (empty ?o - object)
                (filled ?o - object)
                (broken ?o - object)

                (free ?a - arm)
                (grasped ?a - arm ?o - object ?g - grasp_pose)
                (lifted ?a - arm ?o - object)

                (ontable ?o - object ?t - table)
                (ontray ?o - object ?t - tray)

                (reachable ?a - arm ?g - grasp_pose)
                (graspable ?o - object ?g - grasp_pose)

                (unobstructed ?g - grasp_pose)
                (obstructed ?g - grasp_pose ?b - object)
                )

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; grasp actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action grasp
 :parameters   (?a - arm ?o - object ?g - grasp_pose ?t - table)
 :precondition (and (free ?a)(ontable ?o ?t)(graspable ?o ?g)
                    (reachable ?a ?g)(unobstructed ?g))
 :effect       (and (grasped ?a ?o ?g)(not(graspable ?o ?g))(not(free ?a))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; pick up actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action singlearm-pickup
 :parameters   (?a - arm ?o - object ?g - grasp_pose ?t - table)
 :precondition ;(and (grasped ?a ?o ?g)(ontable ?o ?t)(empty ?o)
                    (and 
                        (grasped ?a ?o ?g)(ontable ?o ?t)
                        (exists (?a - arm ?b - object)(lifted ?a ?o))
                        (exists (?a - arm)(and (lifted ?a ?o)(lifted ?a ?o)))
                        (empty ?o)
                        
                    (exists (?b - arm ?p - grasp_pose) 
                        (and (not(= ?a ?b))(not(= ?g ?p))
                            (graspable ?o ?p)(not(grasped ?b ?o ?p))))
                    )
 :effect       (and (lifted ?a ?o)(not(ontable ?o ?t)))
 )


)
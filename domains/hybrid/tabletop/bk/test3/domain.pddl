(define (domain tabletop)

  (:requirements :strips :typing :equality :negative-preconditions :existential-preconditions :universal-preconditions :conditional-effects)

  (:types arm table tray object grasp_pose)

  (:predicates  (empty ?o - object)
                (filled ?o - object)
                (broken ?o - object)

                (free ?a - arm)
                (grasped ?a - arm ?o - object ?g - grasp_pose)
                (lifted ?o - object)

                (ontable ?o - object ?t - table)
                (ontray ?o - object ?t - tray)

                (reachable ?a - arm ?g - grasp_pose)
                (graspable ?o - object ?g - grasp_pose)
                (ungrasped ?g - grasp_pose)

                (unobstructed ?g - grasp_pose)
                (obstructed ?g - grasp_pose ?b - object)
                )

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; grasp actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action grasp
 :parameters   (?a - arm ?o - object ?g - grasp_pose ?t - table)
 :precondition (and (free ?a)(ontable ?o ?t)(graspable ?o ?g)(reachable ?a ?g)
                    (ungrasped ?g))
 :effect       (and (grasped ?a ?o ?g)(not(ungrasped ?g))(not(free ?a))))

(:action ungrasp
 :parameters   (?a - arm ?o - object ?g - grasp_pose ?t - table)
 :precondition (and (grasped ?a ?o ?g)(graspable ?o ?g)(ontable ?o ?t))
 :effect       (and (free ?a)(ungrasped ?g)(not(grasped ?a ?o ?g))))

(:action singlearm-pickup
 :parameters   (?a - arm ?o - object ?g1 ?g2 ?g3 - grasp_pose ?t - table)
 :precondition (and (grasped ?a ?o ?g1)(ontable ?o ?t)(empty ?o)
                    (graspable ?o ?g1)(graspable ?o ?g2)(graspable ?o ?g3)
                    (ungrasped ?g2)(ungrasped ?g3)
                    (not(= ?g1 ?g2))(not(= ?g2 ?g3))
               )
 :effect       (and (lifted ?o)(not(ontable ?o ?t))
                    ))

(:action dualarm-pickup
 :parameters   (?a ?b - arm ?o - object ?g1 ?g2 ?g3 - grasp_pose ?t - table)
 :precondition (and (grasped ?a ?o ?g1)(grasped ?b ?o ?g2)(ontable ?o ?t)(empty ?o)
                    (graspable ?o ?g1)(graspable ?o ?g2)(graspable ?o ?g3)
                    (ungrasped ?g3)(not(= ?g1 ?g2))(not(= ?g2 ?g3))
                    (not(= ?a ?b))
               )
 :effect       (and (lifted ?o)(not(ontable ?o ?t))
                    ))


)
(define (domain tabletop)

  (:requirements :strips :typing :equality :negative-preconditions :existential-preconditions :universal-preconditions :conditional-effects)

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
 :precondition (and (free ?a)(ontable ?o ?t)(graspable ?o ?g)(reachable ?a ?g)
                    (forall (?b - object) (not(obstructed ?g ?b))))
 :effect       (and (grasped ?a ?o ?g)(not(graspable ?o ?g))(not(free ?a))))

; (:action grasp
;  :parameters   (?a - arm ?o - object ?g - grasp_pose ?t - table)
;  :precondition (and (free ?a)(ontable ?o ?t)(graspable ?o ?g)
;                     (reachable ?a ?g)(unobstructed ?g))
;  :effect       (and (grasped ?a ?o ?g)(not(graspable ?o ?g))(not(free ?a))))

(:action ungrasp
 :parameters   (?a - arm ?o - object ?g - grasp_pose ?t - table)
 :precondition (and (grasped ?a ?o ?g)(ontable ?o ?t))
 :effect       (and (free ?a)(graspable ?o ?g)(not(grasped ?a ?o ?g))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; pick up actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action singlearm-pickup
 :parameters   (?a - arm ?o - object ?g - grasp_pose ?t - table)
 :precondition (and (grasped ?a ?o ?g)(ontable ?o ?t)(empty ?o)
                    (exists (?b - arm ?p - grasp_pose) 
                        (and (not(= ?a ?b))(not(= ?g ?p))(graspable ?o ?p)(not(grasped ?b ?o ?p)))))
 :effect       (and (lifted ?a ?o)(not(ontable ?o ?t))
                    (forall (?p - grasp_pose) 
                            (when (obstructed ?p ?o) (not(obstructed ?p ?o))))
                    ))

(:action dualarm-pickup
 :parameters   (?a ?b - arm ?o - object ?g1 ?g2 - grasp_pose ?t - table)
 :precondition (and (grasped ?a ?o ?g1)(grasped ?b ?o ?g2);(filled ?o)
                    (ontable ?o ?t)(not(= ?a ?b)))
 :effect       (and (lifted ?a ?o)(lifted ?b ?o)(not(ontable ?o ?t))
                    (forall (?p - grasp_pose) 
                            (when (obstructed ?p ?o) (not(obstructed ?p ?o))))
                    ))

; (:action singlearm-pickup
;  :parameters   (?a - arm ?o - object ?g - grasp_pose ?t - table)
;  :precondition (and (grasped ?a ?o ?g)(ontable ?o ?t)(empty ?o)
;                     (exists (?b - arm ?p - grasp_pose) 
;                         (and (not(= ?a ?b))(not(= ?g ?p))(graspable ?o ?p)(not(grasped ?b ?o ?p)))))
;  :effect       (and (lifted ?a ?o)(not(ontable ?o ?t))))

; (:action dualarm-pickup
;  :parameters   (?a ?b - arm ?o - object ?g1 ?g2 - grasp_pose ?t - table)
;  :precondition (and (grasped ?a ?o ?g1)(grasped ?b ?o ?g2);(filled ?o)
;                     (ontable ?o ?t)(not(= ?a ?b)))
;  :effect       (and (lifted ?a ?o)(lifted ?b ?o)(not(ontable ?o ?t))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; put down actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action put-on-table
 :parameters   (?a - arm ?o - object ?g - grasp_pose ?t - table)
 :precondition (and (grasped ?a ?o ?g)(lifted ?a ?o)
                    (exists (?b - arm) (and (not(= ?a ?b))(not(lifted ?b ?o)))))
 :effect       (and (ontable ?o ?t)(graspable ?o ?g)(free ?a)
                    (not(grasped ?a ?o ?g))(not(lifted ?a ?o))))

(:action put-on-tray
 :parameters   (?a - arm ?o - object ?g - grasp_pose ?t - tray)
 :precondition (and (grasped ?a ?o ?g)(lifted ?a ?o)
                    (exists (?b - arm) (and (not(= ?a ?b))(not(lifted ?b ?o)))))
 :effect       (and (ontray ?o ?t)(graspable ?o ?g)(free ?a)
                    (not(grasped ?a ?o ?g))(not(lifted ?a ?o))))

(:action dualarm-put-on-table
 :parameters   (?a ?b - arm ?o - object ?g1 ?g2 - grasp_pose ?t - table)
 :precondition (and (grasped ?a ?o ?g1)(grasped ?b ?o ?g2)(lifted ?a ?o)(lifted ?b ?o)(not(= ?a ?b)))
 :effect       (and (ontable ?o ?t)(graspable ?o ?g1)(graspable ?o ?g2)
                    (free ?a)(free ?b)(not(grasped ?a ?o ?g1))
                    (not(grasped ?b ?o ?g2))(not(lifted ?a ?o))(not(lifted ?b ?o))))

(:action dualarm-put-on-tray
 :parameters   (?a ?b - arm ?o - object ?g1 ?g2 - grasp_pose ?t - tray)
 :precondition (and (grasped ?a ?o ?g1)(grasped ?b ?o ?g2)(lifted ?a ?o)(lifted ?b ?o)(not(= ?a ?b)))
 :effect       (and (ontray ?o ?t)(graspable ?o ?g1)(graspable ?o ?g2)
                    (free ?a)(free ?b)(not(grasped ?a ?o ?g1))
                    (not(grasped ?b ?o ?g2))(not(lifted ?a ?o))(not(lifted ?b ?o))))

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
(define (domain tabletop)

  (:requirements :strips :typing :equality :negative-preconditions :universal-preconditions :conditional-effects :probabilistic-effects)

  (:types arm table tray object grasp_pose)

  (:predicates  (empty ?o - object)
                (filled ?o - object)
                (broken ?o - object)

                (free ?a - arm)
                (grasped ?a - arm ?o - object ?g - grasp_pose)
                (lifted ?o - object)
                (co_lifted ?o - object)

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

; (:action grasp
;  :parameters   (?a - arm ?o - object ?g - grasp_pose ?t - table)
;  :precondition (and (free ?a)(ontable ?o ?t)(graspable ?o ?g)
;                     (reachable ?a ?g)(unobstructed ?g))
;  :effect       (and (grasped ?a ?o ?g)(not(graspable ?o ?g))(not(free ?a))))

(:action grasp
 :parameters   (?a - arm ?o - object ?g - grasp_pose ?t - table)
 :precondition (and (free ?a)(ontable ?o ?t)(graspable ?o ?g)(reachable ?a ?g)
                    (forall (?x - object) (not(obstructed ?g ?x))))
 :effect       (and (grasped ?a ?o ?g)(not(graspable ?o ?g))(not(free ?a))))

(:action ungrasp
 :parameters   (?a - arm ?o - object ?g - grasp_pose ?t - table)
 :precondition (and (grasped ?a ?o ?g)(ontable ?o ?t))
 :effect       (and (free ?a)(graspable ?o ?g)(not(grasped ?a ?o ?g))))

; (:action weigh
;  :parameters   (?a - arm ?o - object ?g - grasp_pose ?t - table)
;  :precondition (and (grasped ?a ?o ?g)(ontable ?o ?t))
;  :effect       (and (oneof (empty ?o)(filled ?o))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; pick up actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action pickup-empty
 :parameters   (?a - arm ?o - object ?g1 ?g2 ?g3 - grasp_pose ?t - table)
 :precondition (and (grasped ?a ?o ?g1)(ontable ?o ?t)(empty ?o)
                    (graspable ?o ?g2)(graspable ?o ?g3)
                    (not(= ?g1 ?g2))(not(= ?g2 ?g3)))
 :effect       (probabilistic
                    4/5 (and (lifted ?o)(not(ontable ?o ?t))
                            (forall (?p - grasp_pose)
                                (when (obstructed ?p ?o) (not(obstructed ?p ?o)))))
                    1/5 (and (ontable ?o ?t)(free ?a)(graspable ?o ?g1)(not(grasped ?a ?o ?g1)))))

(:action pickup-filled
 :parameters   (?a - arm ?o - object ?g1 ?g2 ?g3 - grasp_pose ?t - table)
 :precondition (and (grasped ?a ?o ?g1)(ontable ?o ?t)(filled ?o)
                    (graspable ?o ?g2)(graspable ?o ?g3)
                    (not(= ?g1 ?g2))(not(= ?g2 ?g3)))
 :effect       (probabilistic
                    3/5 (and (lifted ?o)(not(ontable ?o ?t))
                             (forall (?p - grasp_pose)
                                (when (obstructed ?p ?o) (not(obstructed ?p ?o)))))
                    1/5 (and (ontable ?o ?t)(free ?a)(graspable ?o ?g1)(not(grasped ?a ?o ?g1)))
                    1/5 (and (ontable ?o ?t)(free ?a)(graspable ?o ?g1)(not(grasped ?a ?o ?g1))(not(filled ?o))(empty ?o))))

(:action dualarm-pickup
 :parameters   (?a ?b - arm ?o - object ?g1 ?g2 ?g3 - grasp_pose ?t - table)
 :precondition (and (grasped ?a ?o ?g1)(grasped ?b ?o ?g2)(ontable ?o ?t)
                    (graspable ?o ?g3)(not(= ?g1 ?g2))(not(= ?g2 ?g3))(not(= ?a ?b)))
 :effect       (and (co_lifted ?o)(not(ontable ?o ?t))
                    (forall (?p - grasp_pose)
                         (when (obstructed ?p ?o) (not(obstructed ?p ?o))))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; put down actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action put-on-table
 :parameters   (?a - arm ?o - object ?g - grasp_pose ?t - table)
 :precondition (and (grasped ?a ?o ?g)(lifted ?o))
 :effect       (and (ontable ?o ?t)(graspable ?o ?g)(free ?a)
                    (not(grasped ?a ?o ?g))(not(lifted ?o))))

(:action put-on-tray
 :parameters   (?a - arm ?o - object ?g - grasp_pose ?t - tray)
 :precondition (and (grasped ?a ?o ?g)(lifted ?o))
 :effect       (and (ontray ?o ?t)(graspable ?o ?g)(free ?a)
                    (not(grasped ?a ?o ?g))(not(lifted ?o))))

(:action dualarm-put-on-table
 :parameters   (?a ?b - arm ?o - object ?g1 ?g2 - grasp_pose ?t - table)
 :precondition (and (grasped ?a ?o ?g1)(grasped ?b ?o ?g2)(co_lifted ?o)(not(= ?a ?b)))
 :effect       (and (ontable ?o ?t)(graspable ?o ?g1)(graspable ?o ?g2)
                    (free ?a)(free ?b)(not(grasped ?a ?o ?g1))
                    (not(grasped ?b ?o ?g2))(not(co_lifted ?o))))

(:action dualarm-put-on-tray
 :parameters   (?a ?b - arm ?o - object ?g1 ?g2 - grasp_pose ?t - tray)
 :precondition (and (grasped ?a ?o ?g1)(grasped ?b ?o ?g2)(co_lifted ?o)(not(= ?a ?b)))
 :effect       (and (ontray ?o ?t)(graspable ?o ?g1)(graspable ?o ?g2)
                    (free ?a)(free ?b)(not(grasped ?a ?o ?g1))
                    (not(grasped ?b ?o ?g2))(not(co_lifted ?o))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; actions to delete constraints in a state upon happening some other actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; (:action unobstructed
;  :parameters   (?g - grasp_pose ?o - object)
;  :precondition (and (obstructed ?g ?o)(lifted ?o))
;  :effect       (and (not(obstructed ?g ?o))(unobstructed ?g)))

; (:action unobstructed2
;  :parameters   (?g - grasp_pose ?o - object)
;  :precondition (and (obstructed ?g ?o)(co_lifted ?o))
;  :effect       (and (not(obstructed ?g ?o))(unobstructed ?g)))

)
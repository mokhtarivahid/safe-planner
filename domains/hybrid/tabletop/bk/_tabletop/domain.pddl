(define (domain tabletop)

  (:requirements :strips :typing :equality :probabilistic-effects)

  (:types arm table tray object grasp_pose)

  (:predicates  (empty ?o - object)
                (filled ?o - object)
                (broken ?o - object)

                (free ?a - arm)
                (grasped ?a - arm ?o - object ?g - grasp_pose)
                (lifted ?a - arm ?o - object)
                (co_lifted ?a ?b  - arm ?o - object)

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

(:action ungrasp
 :parameters   (?a - arm ?o - object ?g - grasp_pose ?t - table)
 :precondition (and (grasped ?a ?o ?g)(ontable ?o ?t))
 :effect       (and (free ?a)(graspable ?o ?g)(not(grasped ?a ?o ?g))))

; (:action weigh
;  :parameters   (?a - arm ?o - object ?g - grasp_pose ?t - table)
;  :precondition (and (grasped ?a ?o ?g)(ontable ?o ?t))
;  :effect       (and (probabilistic 1/2 (empty ?o))
;                     (probabilistic 1/2 (filled ?o))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; pick up actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; (:action pickup-empty
;  :parameters   (?a - arm ?o - object ?g1 ?g2 ?g3 - grasp_pose ?t - table)
;  :precondition (and (grasped ?a ?o ?g1)(ontable ?o ?t)(empty ?o)
;                     (graspable ?o ?g2)(graspable ?o ?g3)
;                     (not(= ?g1 ?g2))(not(= ?g2 ?g3)))
;  :effect       (and (probabilistic 1/2 (and (lifted ?a ?o)(not(ontable ?o ?t))))
;                     (probabilistic 1/2 (and (ontable ?o ?t)(free ?a)(graspable ?o ?g1)(not(grasped ?a ?o ?g1))))))

; (:action pickup-filled
;  :parameters   (?a - arm ?o - object ?g1 ?g2 ?g3 - grasp_pose ?t - table)
;  :precondition (and (grasped ?a ?o ?g1)(ontable ?o ?t)(filled ?o)
;                     (graspable ?o ?g2)(graspable ?o ?g3)
;                     (not(= ?g1 ?g2))(not(= ?g2 ?g3)))
;  :effect       (and (probabilistic 1/3 (and (lifted ?a ?o)(not(ontable ?o ?t))))
;                     (probabilistic 1/3 (and (ontable ?o ?t)(free ?a)(graspable ?o ?g1)(not(grasped ?a ?o ?g1))))
;                     (probabilistic 1/3 (and (ontable ?o ?t)(free ?a)(graspable ?o ?g1)(not(grasped ?a ?o ?g1))(not(filled ?o))(empty ?o)))))

; (:action dualarm-pickup
;  :parameters   (?a ?b - arm ?o - object ?g1 ?g2 ?g3 - grasp_pose ?t - table)
;  :precondition (and (grasped ?a ?o ?g1)(grasped ?b ?o ?g2)(ontable ?o ?t)
;                     (graspable ?o ?g3)(not(= ?g1 ?g2))(not(= ?g2 ?g3))(not(= ?a ?b)))
;  :effect       (and (co_lifted ?a ?b ?o)(not(ontable ?o ?t))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action pickup-empty2
 :parameters   (?a - arm ?o - object ?g1 ?g2 - grasp_pose ?t - table)
 :precondition (and (grasped ?a ?o ?g1)(ontable ?o ?t)(empty ?o)
                    (graspable ?o ?g2)(not(= ?g1 ?g2)))
 :effect       (and (probabilistic 1/2 (and (lifted ?a ?o)(not(ontable ?o ?t))))
                    (probabilistic 1/2 (and (ontable ?o ?t)(free ?a)(graspable ?o ?g1)(not(grasped ?a ?o ?g1))))))

(:action pickup-filled2
 :parameters   (?a - arm ?o - object ?g1 ?g2 - grasp_pose ?t - table)
 :precondition (and (grasped ?a ?o ?g1)(ontable ?o ?t)(filled ?o)
                    (graspable ?o ?g2)(not(= ?g1 ?g2)))
 :effect       (and (probabilistic 1/3 (and (lifted ?a ?o)(not(ontable ?o ?t))))
                    (probabilistic 1/3 (and (ontable ?o ?t)(free ?a)(graspable ?o ?g1)(not(grasped ?a ?o ?g1))))
                    (probabilistic 1/3 (and (ontable ?o ?t)(free ?a)(graspable ?o ?g1)(not(grasped ?a ?o ?g1))(not(filled ?o))(empty ?o)))))

(:action dualarm-pickup2
 :parameters   (?a ?b - arm ?o - object ?g1 ?g2 - grasp_pose ?t - table)
 :precondition (and (grasped ?a ?o ?g1)(grasped ?b ?o ?g2)(ontable ?o ?t)
                    (not(= ?g1 ?g2))(not(= ?a ?b)))
 :effect       (and (co_lifted ?a ?b ?o)(not(ontable ?o ?t))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; put down actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action put-on-table
 :parameters   (?a - arm ?o - object ?g - grasp_pose ?t - table)
 :precondition (and (grasped ?a ?o ?g)(lifted ?a ?o))
 :effect       (and (ontable ?o ?t)(graspable ?o ?g)(free ?a)
                    (not(grasped ?a ?o ?g))(not(lifted ?a ?o))))

(:action put-on-tray
 :parameters   (?a - arm ?o - object ?g - grasp_pose ?t - tray)
 :precondition (and (grasped ?a ?o ?g)(lifted ?a ?o))
 :effect       (and (ontray ?o ?t)(graspable ?o ?g)(free ?a)
                    (not(grasped ?a ?o ?g))(not(lifted ?a ?o))))

(:action dualarm-put-on-table
 :parameters   (?a ?b - arm ?o - object ?g1 ?g2 - grasp_pose ?t - table)
 :precondition (and (grasped ?a ?o ?g1)(grasped ?b ?o ?g2)(co_lifted ?a ?b ?o)(not(= ?a ?b)))
 :effect       (and (ontable ?o ?t)(graspable ?o ?g1)(graspable ?o ?g2)
                    (free ?a)(free ?b)(not(grasped ?a ?o ?g1))
                    (not(grasped ?b ?o ?g2))(not(co_lifted ?a ?b ?o))))

(:action dualarm-put-on-tray
 :parameters   (?a ?b - arm ?o - object ?g1 ?g2 - grasp_pose ?t - tray)
 :precondition (and (grasped ?a ?o ?g1)(grasped ?b ?o ?g2)(co_lifted ?a ?b ?o)(not(= ?a ?b)))
 :effect       (and (ontray ?o ?t)(graspable ?o ?g1)(graspable ?o ?g2)
                    (free ?a)(free ?b)(not(grasped ?a ?o ?g1))
                    (not(grasped ?b ?o ?g2))(not(co_lifted ?a ?b ?o))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; actions to delete constraints in a state upon happening some other actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action unobstructed
 :parameters   (?g - grasp_pose ?o - object)
 :precondition (and (obstructed ?g ?o)(lifted ?o))
 :effect       (and (not(obstructed ?g ?o))(unobstructed ?g)))

(:action unobstructed2
 :parameters   (?g - grasp_pose ?o - object)
 :precondition (and (obstructed ?g ?o)(co_lifted ?o))
 :effect       (and (not(obstructed ?g ?o))(unobstructed ?g)))

)
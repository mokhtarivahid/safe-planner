(define (domain tabletop)

  (:requirements :strips :typing :equality :negative-preconditions)

  (:types arm table tray object grasp_pose)

  (:predicates  (empty ?o - object)
                (filled ?o - object)
                (broken ?o - object)

                (free ?a - arm)
                (grasped ?a - arm ?o - object ?g - grasp_pose)
                (lifted ?a - arm ?o - object)
                ; (co_lifted ?o - object)
                ; (start_lifting ?a - arm ?o - object)
                ; (start_putting_on_tray ?a - arm ?o - object)

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

(:action singlearm-pickup
 :parameters   (?a - arm ?o - object ?g - grasp_pose ?t - table)
 :precondition (and (grasped ?a ?o ?g)(ontable ?o ?t)(empty ?o)
                    (exists (?b - arm ?p - grasp_pose) 
                        (and (not(= ?a ?b))(not(= ?g ?p))(graspable ?o ?p)(not(grasped ?b ?o ?p)))))
 :effect       (and (lifted ?a ?o)(not(ontable ?o ?t))))

; (:action pickup-filled
;  :parameters   (?a - arm ?o - object ?g - grasp_pose ?t - table)
;  :precondition (and (grasped ?a ?o ?g)(ontable ?o ?t)(filled ?o))
;  :effect       (and (probabilistic 1/3 (and (lifted ?a ?o)(not(ontable ?o ?t))))
;                     (probabilistic 1/3 (and (ontable ?o ?t)(free ?a)(not(grasped ?a ?o ?g))))
;                     (probabilistic 1/3 (and (ontable ?o ?t)(free ?a)(not(grasped ?a ?o ?g))(not(filled ?o))(empty ?o)))))

; (:action start-lifting
;  :parameters   (?a - arm ?o - object ?g - grasp_pose ?t - table)
;  :precondition (and (grasped ?a ?o ?g)(ontable ?o ?t)(not(start_lifting ?a ?o))
;                     (exists (?b - arm ?p - grasp_pose) 
;                         (and (not(= ?a ?b))(not(= ?g ?p))(grasped ?b ?o ?p))))
;  :effect       (and (start_lifting ?a ?o)))


; (:action dualarm-picked-up
;  :parameters   (?a ?b - arm ?o - object ?t - table)
;  :precondition (and (start_lifting ?a ?o)(start_lifting ?b ?o)
;                     (ontable ?o ?t)(not(= ?a ?b)))
;  :effect       (and (lifted ?a ?o)(lifted ?b ?o)(not(ontable ?o ?t))
;                     (not(start_lifting ?a ?o))(not(start_lifting ?b ?o))))

; (:action dualarm-pickup
;  :parameters   (?a ?b - arm ?o - object ?t - table)
;  :precondition (and (start_lifting ?a ?o)(start_lifting ?b ?o)
;                     (ontable ?o ?t)(not(= ?a ?b)))
;  :effect       (and (lifted ?a ?o)(lifted ?b ?o)(not(ontable ?o ?t))
;                     (not(start_lifting ?a ?o))(not(start_lifting ?b ?o))))

(:action dualarm-pickup
 :parameters   (?a ?b - arm ?o - object ?g1 ?g2 - grasp_pose ?t - table)
 :precondition (and (grasped ?a ?o ?g1)(grasped ?b ?o ?g2);(filled ?o)
                    (ontable ?o ?t)(not(= ?a ?b)))
 :effect       (and (lifted ?a ?o)(lifted ?b ?o)(not(ontable ?o ?t))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; put down actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action put-on-table
 :parameters   (?a - arm ?o - object ?g - grasp_pose ?t - table)
 :precondition (and (grasped ?a ?o ?g)(lifted ?a ?o)
                    (exists (?b - arm) 
                        (and (not(= ?a ?b))(not(lifted ?b ?o)))))
 :effect       (and (ontable ?o ?t)(graspable ?o ?g)(free ?a)
                    (not(grasped ?a ?o ?g))(not(lifted ?a ?o))))

(:action put-on-tray
 :parameters   (?a - arm ?o - object ?g - grasp_pose ?t - tray)
 :precondition (and (grasped ?a ?o ?g)(lifted ?a ?o)
                    (exists (?b - arm) 
                        (and (not(= ?a ?b))(not(lifted ?b ?o)))))
 :effect       (and (ontray ?o ?t)(graspable ?o ?g)(free ?a)
                    (not(grasped ?a ?o ?g))(not(lifted ?a ?o))))

(:action dualarm-put-on-table
 :parameters   (?a ?b - arm ?o - object ?g1 ?g2 - grasp_pose ?t - table)
 :precondition (and (grasped ?a ?o ?g1)(grasped ?b ?o ?g2)(lifted ?a ?o)(lifted ?b ?o)(not(= ?a ?b)))
 :effect       (and (ontable ?o ?t)(graspable ?o ?g1)(graspable ?o ?g2)
                    (free ?a)(free ?b)(not(grasped ?a ?o ?g1))
                    (not(grasped ?b ?o ?g2))(not(lifted ?a ?o))(not(lifted ?b ?o))))

; (:action start-putting-on-tray
;  :parameters   (?a - arm ?o - object ?t - tray)
;  :precondition (and (lifted ?a ?o)
;                     (exists (?b - arm) (and (not(= ?a ?b))(lifted ?b ?o))))
;  :effect       (and (start_putting_on_tray ?a ?o)))

; (:action dualarm-putdown-on-tray
;  :parameters   (?a ?b - arm ?o - object ?g1 ?g2 - grasp_pose ?t - tray)
;  :precondition (and (start_putting_on_tray ?a ?o)(start_putting_on_tray ?b ?o)
;                     (grasped ?a ?o ?g1)(grasped ?b ?o ?g2)(lifted ?a ?o)(lifted ?b ?o)(not(= ?a ?b)))
;  :effect       (and (ontray ?o ?t)(graspable ?o ?g1)(graspable ?o ?g2)
;                     (free ?a)(free ?b)(not(grasped ?a ?o ?g1))
;                     (not(grasped ?b ?o ?g2))(not(lifted ?a ?o))(not(lifted ?b ?o))
;                     (not(start_putting_on_tray ?a ?o))(not(start_putting_on_tray ?b ?o))))


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
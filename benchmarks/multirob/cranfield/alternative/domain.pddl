;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Cranfield assembly domain
;; Planners supporting derived-predicates: FF-X, LPG-TD, FD (additive heuristic)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(define (domain cranfield)

(:requirements :strips :typing :equality :derived-predicates :disjunctive-preconditions)

(:types 
        faceplate table - place
        graspable robot_pos square_peg_pos round_peg_pos shaft_pos pendulum_pos spacer_pos - position
        peg shaft pendulum spacer - graspable
        square_peg round_peg - peg
        robot)

(:predicates  
              (reachable ?p - position) ;; position is unoccupied (free) to reach

              (empty ?p - position ?c - place) ;; no object is in the position

              (robot_at ?r - robot ?p - position ?c - place)
              (arm_gripped ?r - robot ?o - graspable)
              (arm_free ?r - robot)

              (object_at ?o - graspable ?p - position ?c - place)
              (inserted ?o - graspable ?f - faceplate)

              ; axioms (constraint)
              (can_grip ?o - graspable)
              (can_insert ?o - graspable ?s - position ?f - faceplate)
              (can_fit ?o - graspable ?s - position ?f - place)

              ; assembly axioms
              (cranfield_assembled ?f - faceplate)
              (cranfield_disassembled_to ?p - place)
              (cranfield_disassembled ?f - faceplate)
)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; constraint on ordering of grasp:
;; 1) all graspable can be grasped from a table without any constraint
;; 2) round_peg, pendulum and spacer can be grasped without any constraint
;; 3) shaft can only be grasped when pendulum was already removed (grasped)
;; 4) square_peg can only be grasped when spacer was already removed (grasped)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:derived (can_grip ?o - graspable)
    (or 
        (exists (?p - position ?f - table) (object_at ?o ?p ?f))
        (exists (?p - pendulum_pos ?f - faceplate) (object_at ?o ?p ?f))
        (exists (?p - round_peg_pos ?f - faceplate) (object_at ?o ?p ?f))
        (exists (?p - spacer_pos ?f - faceplate) (object_at ?o ?p ?f))
        (exists (?p - shaft_pos ?q - pendulum_pos ?f - faceplate) (and (object_at ?o ?p ?f) (empty ?q ?f)))
        (exists (?p - square_peg_pos ?q - spacer_pos ?f - faceplate) (and (object_at ?o ?p ?f) (empty ?q ?f)))
    )
)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; a constraint on ordering of insertion:
;; 1) round_peg, pendulum and spacer can be inserted without any constraint
;; 2) shaft can only be inserted when pendulum is not inserted
;; 3) square_peg can only be inserted when spacer is not inserted
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:derived (can_insert ?o - graspable ?s - position ?f - faceplate)
    (or
        (exists (?g - round_peg ?p - round_peg_pos) 
            (and (empty ?p ?f) (= ?o ?g) (= ?s ?p)))
        (exists (?g - spacer ?p - spacer_pos) 
            (and (empty ?p ?f) (= ?o ?g) (= ?s ?p)))
        (exists (?g - pendulum ?p - pendulum_pos) 
            (and (empty ?p ?f) (= ?o ?g) (= ?s ?p)))
        (exists (?g - shaft ?p - shaft_pos ?q - pendulum_pos) 
            (and (empty ?p ?f) (empty ?q ?f) (= ?o ?g) (= ?s ?p)))
        (exists (?g - square_peg ?p - square_peg_pos ?q - spacer_pos) 
            (and (empty ?p ?f) (empty ?q ?f) (= ?o ?g) (= ?s ?p)))
    )
)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; a constraint to fit a graspable into its a position of its type
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:derived (can_fit ?o - graspable ?s - position ?f - place)
    (or
        (exists (?g - round_peg ?p - round_peg_pos) (and (empty ?p ?f) (= ?o ?g) (= ?s ?p)))
        (exists (?g - spacer ?p - spacer_pos) (and (empty ?p ?f) (= ?o ?g) (= ?s ?p)))
        (exists (?g - pendulum ?p - pendulum_pos) (and (empty ?p ?f) (= ?o ?g) (= ?s ?p)))
        (exists (?g - shaft ?p - shaft_pos) (and (empty ?p ?f) (= ?o ?g) (= ?s ?p)))
        (exists (?g - square_peg ?p - square_peg_pos) (and (empty ?p ?f) (= ?o ?g) (= ?s ?p)))
    )
)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; assembly axioms (constraints)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:derived (cranfield_assembled ?f - faceplate)
    (and 
        (exists (?o - shaft ?p - shaft_pos) (and (inserted ?o ?f) (object_at ?o ?p ?f)))
        (exists (?o - pendulum ?p - pendulum_pos) (and (inserted ?o ?f) (object_at ?o ?p ?f)))
        (exists (?o - spacer ?p - spacer_pos) (and (inserted ?o ?f) (object_at ?o ?p ?f)))
        (exists (?o1 ?o2 - square_peg ?p1 ?p2 - square_peg_pos) 
            (and (inserted ?o1 ?f) (inserted ?o2 ?f) (object_at ?o1 ?p1 ?f) (object_at ?o2 ?p2 ?f) 
                 (not (= ?o1 ?o2)) (not (= ?p1 ?p2))))
        (exists (?o1 ?o2 - round_peg ?p1 ?p2 - round_peg_pos)
            (and (inserted ?o1 ?f) (inserted ?o2 ?f) (object_at ?o1 ?p1 ?f) (object_at ?o2 ?p2 ?f) 
                 (not (= ?o1 ?o2)) (not (= ?p1 ?p2))))
    )
)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; disassembly axioms (constraints)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:derived (cranfield_disassembled ?f - faceplate)
    (and 
        (exists (?p - shaft_pos) (empty ?p ?f))
        (exists (?p - pendulum_pos) (empty ?p ?f))
        (exists (?p1 ?p2 - square_peg_pos) (and (empty ?p1 ?f) (empty ?p2 ?f) (not (= ?p1 ?p2))))
        (exists (?p1 ?p2 - round_peg_pos) (and (empty ?p1 ?f) (empty ?p2 ?f) (not (= ?p1 ?p2))))
        (exists (?p - spacer_pos) (empty ?p ?f))
    )
)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; disassembly axioms to table/faceplate (constraints)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:derived (cranfield_disassembled_to ?t - place)
    (and 
        (exists (?o - pendulum ?p - pendulum_pos) (object_at ?o ?p ?t))
        (exists (?o - spacer ?p - spacer_pos) (object_at ?o ?p ?t))
        (exists (?o - shaft ?p - shaft_pos) (object_at ?o ?p ?t))
        (exists (?o1 ?o2 - square_peg ?p1 ?p2 - square_peg_pos)
            (and (object_at ?o1 ?p1 ?t) (object_at ?o2 ?p2 ?t) (not (= ?o1 ?o2)) (not (= ?p1 ?p2))))
        (exists (?o1 ?o2 - round_peg ?p1 ?p2 - round_peg_pos)
            (and (object_at ?o1 ?p1 ?t) (object_at ?o2 ?p2 ?t) (not (= ?o1 ?o2)) (not (= ?p1 ?p2))))
    )
)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; robot actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; move/carry actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action move
 :parameters   (?r - robot ?p - position ?x - place ?q - position ?y - place)
 :precondition (and (arm_free ?r) (robot_at ?r ?p ?x) (reachable ?q))
 :effect       (and (robot_at ?r ?q ?y) (not (robot_at ?r ?p ?x)) (reachable ?p) (not (reachable ?q))))

(:action carry
 :parameters   (?r - robot ?p - graspable ?x - place ?q - position ?y - place)
 :precondition (and (arm_gripped ?r ?p) (robot_at ?r ?p ?x) (reachable ?q))
 :effect       (and (robot_at ?r ?q ?y) (not (robot_at ?r ?p ?x)) (reachable ?p) (not (reachable ?q))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; grip/ungrip actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action grip
 :parameters   (?r - robot ?o - graspable ?p - position ?l - place)
 :precondition (and (arm_free ?r) (robot_at ?r ?o ?l) (object_at ?o ?p ?l) (can_grip ?o))
 :effect       (and (arm_gripped ?r ?o) (empty ?p ?l) (not (arm_free ?r)) (not (object_at ?o ?p ?l))))

(:action ungrip
 :parameters   (?r - robot ?o - graspable ?p - position ?l - place)
 :precondition (and (robot_at ?r ?o ?l) (object_at ?o ?p ?l) (arm_gripped ?r ?o))
 :effect       (and (not (arm_gripped ?r ?o)) (arm_free ?r)))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; put/insert actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action put_on_table
 :parameters   (?r - robot ?o - graspable ?p - position ?l - table)
 :precondition (and (robot_at ?r ?p ?l) (arm_gripped ?r ?o) (empty ?p ?l) (can_fit ?o ?p ?l))
 :effect       (and (object_at ?o ?p ?l) (not (robot_at ?r ?p ?l)) (robot_at ?r ?o ?l) (reachable ?p) (not (reachable ?o)) (not (empty ?p ?l))))

(:action insert
 :parameters   (?r - robot ?o - graspable ?p - position ?f - faceplate)
 :precondition (and (robot_at ?r ?p ?f) (arm_gripped ?r ?o) (empty ?p ?f) (can_insert ?o ?p ?f))
 :effect       (and (object_at ?o ?p ?f) (not (robot_at ?r ?p ?f)) (robot_at ?r ?o ?f) (reachable ?p) (not (reachable ?o)) (not (empty ?p ?f)) (inserted ?o ?f)))

)

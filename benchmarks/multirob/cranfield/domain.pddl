;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Cranfield assembly domain
;; Planners supporting derived-predicates: FF-X, LPG-TD, FD (additive heuristic)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(define (domain cranfield)

(:requirements :strips :typing :equality :derived-predicates)

(:types 
        faceplate table - place
        graspable robot_pos square_peg_pos round_peg_pos shaft_pos lever_pos spacer_pos - position
        peg shaft lever spacer - graspable
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

              ; assembly axioms
              (square_pegs_inserted ?f - faceplate)
              (round_pegs_inserted ?f - faceplate)
              (shaft_inserted ?f - faceplate)
              (spacer_inserted ?f - faceplate)
              (lever_inserted ?f - faceplate)
              (cranfield_assembled ?f - faceplate)

              ; disassembly axioms (to table)
              (lever_disassembled_to_table)
              (shaft_disassembled_to_table)
              (square_pegs_disassembled_to_table)
              (round_pegs_disassembled_to_table)
              (spacer_disassembled_to_table)
              (cranfield_disassembled_to_table)

              ; disassembly axioms (from faceplate)
              (shaft_disassembled ?f - faceplate)
              (lever_disassembled ?f - faceplate)
              (round_pegs_disassembled ?f - faceplate)
              (square_pegs_disassembled ?f - faceplate)
              (spacer_disassembled ?f - faceplate)
              (cranfield_disassembled ?f - faceplate)
)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; assembly axioms (constraints)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:derived (shaft_inserted ?f - faceplate)
    (exists (?o - shaft ?p - shaft_pos) (and (inserted ?o ?f) (object_at ?o ?p ?f)))
)

(:derived (lever_inserted ?f - faceplate)
    (and (shaft_inserted ?f) (exists (?o - lever ?p - lever_pos) (and (inserted ?o ?f) (object_at ?o ?p ?f))))
)

(:derived (square_pegs_inserted ?f - faceplate)
    (exists (?o1 ?o2 - square_peg ?p1 ?p2 - square_peg_pos) 
      (and (inserted ?o1 ?f) (inserted ?o2 ?f) (object_at ?o1 ?p1 ?f) (object_at ?o2 ?p2 ?f) (not (= ?o1 ?o2)) (not (= ?p1 ?p2))))
)

(:derived (round_pegs_inserted ?f - faceplate)
    (exists (?o1 ?o2 - round_peg ?p1 ?p2 - round_peg_pos) 
      (and (inserted ?o1 ?f) (inserted ?o2 ?f) (object_at ?o1 ?p1 ?f) (object_at ?o2 ?p2 ?f) (not (= ?o1 ?o2)) (not (= ?p1 ?p2))))
)

(:derived (spacer_inserted ?f - faceplate)
    (and (square_pegs_inserted ?f) (exists (?o - spacer ?p - spacer_pos) (and (inserted ?o ?f) (object_at ?o ?p ?f))))
)

(:derived (cranfield_assembled ?f - faceplate)
    (and (lever_inserted ?f) (spacer_inserted ?f) (round_pegs_inserted ?f))
)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; disassembly axioms to table (constraints)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:derived (lever_disassembled_to_table)
    (exists (?o - lever ?p - lever_pos ?t - table) (object_at ?o ?p ?t))
)

(:derived (spacer_disassembled_to_table)
    (exists (?o - spacer ?p - spacer_pos ?t - table) (object_at ?o ?p ?t))
)

(:derived (shaft_disassembled_to_table)
    (and (lever_disassembled_to_table) (exists (?o - shaft ?p - shaft_pos ?t - table) (object_at ?o ?p ?t)))
)

(:derived (square_pegs_disassembled_to_table)
    (and (spacer_disassembled_to_table)
         (exists (?o1 ?o2 - square_peg ?p1 ?p2 - square_peg_pos ?t - table)
            (and (object_at ?o1 ?p1 ?t) (object_at ?o2 ?p2 ?t) (not (= ?o1 ?o2)) (not (= ?p1 ?p2)))))
)

(:derived (round_pegs_disassembled_to_table)
    (exists (?o1 ?o2 - round_peg ?p1 ?p2 - round_peg_pos ?t - table)
      (and (object_at ?o1 ?p1 ?t) (object_at ?o2 ?p2 ?t) (not (= ?o1 ?o2)) (not (= ?p1 ?p2))))
)

(:derived (cranfield_disassembled_to_table)
    (and (shaft_disassembled_to_table) (square_pegs_disassembled_to_table) (round_pegs_disassembled_to_table))
)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; disassembly axioms (constraints)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:derived (lever_disassembled ?f - faceplate)
    (exists (?p - lever_pos) (empty ?p ?f))
)

(:derived (spacer_disassembled ?f - faceplate)
    (exists (?p - spacer_pos) (empty ?p ?f))
)

(:derived (shaft_disassembled ?f - faceplate)
    (and (lever_disassembled ?f)
         (exists (?p - shaft_pos) (empty ?p ?f)))
)

(:derived (round_pegs_disassembled ?f - faceplate)
    (exists (?p1 ?p2 - round_peg_pos)
        (and (empty ?p1 ?f) (empty ?p2 ?f) (not (= ?p1 ?p2))))
)

(:derived (square_pegs_disassembled ?f - faceplate)
    (and (spacer_disassembled ?f)
         (exists (?p1 ?p2 - square_peg_pos)
              (and (empty ?p1 ?f) (empty ?p2 ?f) (not (= ?p1 ?p2)))))
)

(:derived (cranfield_disassembled ?f - faceplate)
    (and (shaft_disassembled ?f) (square_pegs_disassembled ?f) (round_pegs_disassembled ?f))
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
 :precondition (and (arm_free ?r) (robot_at ?r ?o ?l) (object_at ?o ?p ?l))
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
 :precondition (and (robot_at ?r ?p ?l) (arm_gripped ?r ?o))
 :effect       (and (object_at ?o ?p ?l) (not (robot_at ?r ?p ?l)) (robot_at ?r ?o ?l) (reachable ?p) (not (reachable ?o))))

(:action insert
 :parameters   (?r - robot ?o - graspable ?p - position ?f - faceplate)
 :precondition (and (robot_at ?r ?p ?f) (arm_gripped ?r ?o) (empty ?p ?f))
 :effect       (and (object_at ?o ?p ?f) (not (robot_at ?r ?p ?f)) (robot_at ?r ?o ?f) (reachable ?p) (not (reachable ?o)) (not (empty ?p ?f)) (inserted ?o ?f)))

)

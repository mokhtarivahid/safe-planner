(define (domain pickit)

  (:requirements :strips :typing :probabilistic-effects)

  (:types graspable container camera location arm object)

  (:predicates  
                (arm ?o - arm)
                (camera ?o - object)
                (package ?o - object)
                (box ?o - object)
                (peg ?o - object)
                (hole ?o - object)
                (base ?o - object)
                (cap ?o - object)
                (graspable ?o - object)

                (occupied ?o - object)
                (free ?o - object)

                (arm_canreach ?a - arm ?o - object)
                (arm_vacuumed ?a - arm ?o - object)
                (arm_gripped ?a - arm ?o - object)
                (arm_at ?a - arm ?o - object)
                (arm_free ?a - arm)
                (co_arms ?a1 - arm ?a2 - arm)

                (object_in ?o - object ?c - object)
                (assembled ?o - object ?c - object)
                (ungripped ?o - object)
                (bottom_up ?o - object)
                (top_up ?o - object)
                (camera_checked ?o - object)

                )

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; ABB actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; move/carry actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action move_to_grasp
 :parameters   (?a - arm ?o ?c ?d - object)
 :precondition (and (arm_free ?a) (arm_at ?a ?o) (arm_canreach ?a ?c) (object_in ?c ?d) (graspable ?c) (free ?c))
 :effect       (and (arm_at ?a ?c) (free ?o) (not (occupied ?o)) (occupied ?c) (not (free ?c)) (not (arm_at ?a ?o))))

; (:action carry_object
;  :parameters   (?a - arm ?o ?c ?d - object)
;  :precondition (and (arm_vacuumed ?a ?o) (arm_at ?a ?c) (arm_canreach ?a ?d) (free ?d))
;  :effect       (and (arm_at ?a ?d) (free ?c) (not (occupied ?c)) (occupied ?d) (not (free ?d)) (not (arm_at ?a ?c))))

(:action carry_to_peg
 :parameters   (?a - arm ?o ?c ?d - object)
 :precondition (and (arm_vacuumed ?a ?o) (arm_at ?a ?c) (arm_canreach ?a ?d) (peg ?d) (free ?d))
 :effect       (and (arm_at ?a ?d) (free ?c) (not (occupied ?c)) (occupied ?d) (not (free ?d)) (not (arm_at ?a ?c))))

(:action carry_to_hole
 :parameters   (?a - arm ?o ?c ?d - object)
 :precondition (and (arm_vacuumed ?a ?o) (arm_at ?a ?c) (arm_canreach ?a ?d) (hole ?d) (free ?d))
 :effect       (and (arm_at ?a ?d) (free ?c) (not (occupied ?c)) (occupied ?d) (not (free ?d)) (not (arm_at ?a ?c))))

(:action carry_to_camera
 :parameters   (?a - arm ?o ?c ?d - object)
 :precondition (and (arm_vacuumed ?a ?o) (arm_at ?a ?c) (arm_canreach ?a ?d) (camera ?d) (free ?d))
 :effect       (and (arm_at ?a ?d) (free ?c) (not (occupied ?c)) (occupied ?d) (not (free ?d)) (not (arm_at ?a ?c))))

(:action carry_to_pack
 :parameters   (?a - arm ?o ?c ?d - object)
 :precondition (and (arm_gripped ?a ?o) (arm_at ?a ?c) (arm_canreach ?a ?d) (package ?d) (free ?d))
 :effect       (and (arm_at ?a ?d) (free ?c) (not (occupied ?c)) (occupied ?d) (not (free ?d)) (not (arm_at ?a ?c))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; vacuum/grip actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action vacuum_object
 :parameters   (?a - arm ?o ?c - object)
 :precondition (and (arm_free ?a) (arm_at ?a ?o) (object_in ?o ?c))
 :effect       (and (arm_vacuumed ?a ?o) (arm_at ?a ?c) (occupied ?c) (not (free ?c)) (free ?o) (not (occupied ?o)) (not (arm_at ?a ?o)) (not (arm_free ?a)) (not (object_in ?o ?c))))

(:action grip_object
 :parameters   (?a - arm ?o ?c - object)
 :precondition (and (arm_free ?a) (arm_at ?a ?o) (object_in ?o ?c))
 :effect       (and (arm_gripped ?a ?o) (arm_at ?a ?c) (occupied ?c) (not (free ?c)) (free ?o) (not (occupied ?o)) (not (arm_at ?a ?o)) (not (arm_free ?a)) (not (object_in ?o ?c))))

(:action ungrip_object
 :parameters   (?a - arm ?o1 ?o2 - object)
 :precondition (and (assembled ?o1 ?o2) (arm_gripped ?a ?o2) (base ?o2))
 :effect       (and (arm_free ?a) (ungripped ?o2) (not (arm_gripped ?a ?o2))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; put/place actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action put_in_peg
 :parameters   (?a - arm ?o ?c - object)
 :precondition (and (arm_vacuumed ?a ?o) (arm_at ?a ?c) (bottom_up ?o) (base ?o) (peg ?c))
 :effect       (and (arm_free ?a) (object_in ?o ?c) (not (arm_vacuumed ?a ?o))))

(:action put_in_hole
 :parameters   (?a - arm ?o ?c - object)
 :precondition (and (arm_vacuumed ?a ?o) (arm_at ?a ?c) (bottom_up ?o) (cap ?o) (hole ?c))
 :effect       (and (arm_free ?a) (object_in ?o ?c) (not (arm_vacuumed ?a ?o))))

(:action put_in_pack
 :parameters   (?a - arm ?o ?c - object)
 :precondition (and (arm_gripped ?a ?o) (arm_at ?a ?c) (package ?c) (bottom_up ?o))
 :effect       (and (arm_free ?a) (object_in ?o ?c) (not (arm_gripped ?a ?o)) (not (bottom_up ?o))))
 
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; camera actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action check_bottom_up
 :parameters   (?a - arm ?o ?c - object)
 :precondition (and (arm_vacuumed ?a ?o) (arm_at ?a ?c) (camera ?c))
 :effect (and (camera_checked ?o)
              (probabilistic 0.5 (bottom_up ?o))
              (probabilistic 0.5 (top_up ?o))))

(:action rotate_object
 :parameters   (?a - arm ?o - object)
 :precondition (and (arm_vacuumed ?a ?o) (camera_checked ?o) (top_up ?o))
 :effect       (and (not (top_up ?o)) (bottom_up ?o)))

; (:action rotate_object
;  :parameters   (?a - arm ?o - object)
;  :precondition (and (arm_vacuumed ?a ?o) (camera_checked ?o))
;  :effect       (and (when (not (bottom_up ?o))(bottom_up ?o))))

)
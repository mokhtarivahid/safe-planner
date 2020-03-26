(define (domain pickit)

  (:requirements :strips :typing :conditional-effects :probabilistic-effects)

  (:types graspable container camera object location arm)
  ; (:types arm object)

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
                (pose ?o - object)

                (in_use ?o - object)
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
                (downward ?o - object)
                (upward ?o - object)
                (unknown_pos ?o - object)
                (camera_checked ?o - object)

                (packed ?o1 - object ?o2 - object ?d - object)
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
 :effect       (and (arm_at ?a ?c) (free ?o) (not (in_use ?o)) (in_use ?c) (not (free ?c)) (not (arm_at ?a ?o))))

; (:action carry_object
;  :parameters   (?a - arm ?o ?c ?d - object)
;  :precondition (and (arm_vacuumed ?a ?o) (arm_at ?a ?c) (arm_canreach ?a ?d) (free ?d))
;  :effect       (and (arm_at ?a ?d) (free ?c) (not (in_use ?c)) (in_use ?d) (not (free ?d)) (not (arm_at ?a ?c))))

(:action carry_to_peg
 :parameters   (?a - arm ?o ?c ?d - object)
 :precondition (and (arm_vacuumed ?a ?o) (arm_at ?a ?c) (arm_canreach ?a ?d) (peg ?d) (free ?d))
 :effect       (and (arm_at ?a ?d) (free ?c) (not (in_use ?c)) (in_use ?d) (not (free ?d)) (not (arm_at ?a ?c))))

(:action carry_to_hole
 :parameters   (?a - arm ?o ?c ?d - object)
 :precondition (and (arm_vacuumed ?a ?o) (arm_at ?a ?c) (arm_canreach ?a ?d) (hole ?d) (free ?d))
 :effect       (and (arm_at ?a ?d) (free ?c) (not (in_use ?c)) (in_use ?d) (not (free ?d)) (not (arm_at ?a ?c))))

(:action carry_to_camera
 :parameters   (?a - arm ?o ?c ?d - object)
 :precondition (and (arm_vacuumed ?a ?o) (arm_at ?a ?c) (arm_canreach ?a ?d) (camera ?d) (free ?d))
 :effect       (and (arm_at ?a ?d) (free ?c) (not (in_use ?c)) (in_use ?d) (not (free ?d)) (not (arm_at ?a ?c))))

(:action carry_to_assemble
 :parameters   (?a - arm ?o ?c ?d - object)
 :precondition (and (arm_gripped ?a ?o) (arm_at ?a ?c) (arm_canreach ?a ?d) (pose ?d) (free ?d))
 :effect       (and (arm_at ?a ?d) (free ?c) (not (in_use ?c)) (in_use ?d) (not (free ?d)) (not (arm_at ?a ?c))))

(:action carry_to_pack
 :parameters   (?a - arm ?o1 ?o2 ?s ?d - object)
 :precondition (and (assembled ?o1 ?o2) (arm_gripped ?a ?o1) ;(can_packed ?o1) 
                    (arm_at ?a ?s) (arm_canreach ?a ?d) (package ?d) (free ?d) (ungripped ?o2))
 :effect       (and (arm_at ?a ?d) (free ?s) (not (in_use ?s)) (in_use ?d) (not (free ?d)) (not (arm_at ?a ?s))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; vacuum/grip actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action vacuum_object
 :parameters   (?a - arm ?o ?c - object)
 :precondition (and (arm_free ?a) (arm_at ?a ?o) (object_in ?o ?c))
 :effect       (and (arm_vacuumed ?a ?o) (arm_at ?a ?c) (in_use ?c) (not (free ?c)) (free ?o) (not (in_use ?o)) (not (arm_at ?a ?o)) (not (arm_free ?a)) (not (object_in ?o ?c))))

(:action grip_object
 :parameters   (?a - arm ?o ?c - object)
 :precondition (and (arm_free ?a) (arm_at ?a ?o) (object_in ?o ?c))
 :effect       (and (arm_gripped ?a ?o) (arm_at ?a ?c) (in_use ?c) (not (free ?c)) (free ?o) (not (in_use ?o)) (not (arm_at ?a ?o)) (not (arm_free ?a)) (not (object_in ?o ?c))))

(:action ungrip_object
 :parameters   (?a - arm ?o1 ?o2 - object)
 :precondition (and (assembled ?o1 ?o2) (arm_gripped ?a ?o2) (base ?o2))
 :effect       (and (arm_free ?a) (ungripped ?o2) (not (arm_gripped ?a ?o2))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; put/place actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action put_in_peg
 :parameters   (?a - arm ?o ?c - object)
 :precondition (and (arm_vacuumed ?a ?o) (arm_at ?a ?c) (downward ?o) (base ?o) (peg ?c))
 :effect       (and (arm_free ?a) (object_in ?o ?c) (not (arm_vacuumed ?a ?o)) (not (downward ?o))))

(:action put_in_hole
 :parameters   (?a - arm ?o ?c - object)
 :precondition (and (arm_vacuumed ?a ?o) (arm_at ?a ?c) (downward ?o) (cap ?o) (hole ?c))
 :effect       (and (arm_free ?a) (object_in ?o ?c) (not (arm_vacuumed ?a ?o)) (not (downward ?o))))

(:action put_in_pack
 :parameters   (?a - arm ?o1 ?o2 ?s - object)
 :precondition (and (assembled ?o1 ?o2) (arm_gripped ?a ?o1) (ungripped ?o2) (arm_at ?a ?s) (package ?s))
 :effect       (and (packed ?o1 ?o2 ?s) (arm_free ?a) (not (arm_gripped ?a ?o1))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; camera actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action check_orientation
 :parameters   (?a - arm ?o ?c - object)
 :precondition (and (arm_vacuumed ?a ?o) (arm_at ?a ?c) (camera ?c) (unknown_pos ?o))
 :effect (and (camera_checked ?o)
              (oneof (and (downward ?o) (not (unknown_pos ?o)))
                     (and (upward ?o) (not (unknown_pos ?o))))))

; (:action rotate_object
;  :parameters   (?a - arm ?o - object)
;  :precondition (and (arm_vacuumed ?a ?o) (camera_checked ?o))
;  :effect (and (when (downward ?o) (and (not (downward ?o)) (upward ?o)))
;               (when (upward ?o) (and (not (upward ?o)) (downward ?o)))))

(:action rotate_object
 :parameters   (?a - arm ?o - object)
 :precondition (and (arm_vacuumed ?a ?o) (camera_checked ?o) (upward ?o))
 :effect       (and (not (upward ?o)) (downward ?o)))

(:action rotate_object
 :parameters   (?a - arm ?o - object)
 :precondition (and (arm_vacuumed ?a ?o) (camera_checked ?o) (downward ?o))
 :effect       (and (not (downward ?o)) (upward ?o)))


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; assemble actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;;; pack from cap on top and base on bottom, that is, the arm holding the 
;;; base should ungrip (release) it, and the arm holding cap should pack 
;;; the assembled objects.
(:action assemble
 :parameters   (?a1 ?a2 - arm ?o1 ?o2 ?p1 ?p2 - object)
 :precondition (and (arm_gripped ?a1 ?o1) (arm_at ?a1 ?p1) (pose ?p1) (co_arms ?a1 ?a2) ;(arm_canreach ?a1 ?p) (package ?p) 
                    (arm_gripped ?a2 ?o2) (arm_at ?a2 ?p2) (pose ?p2) (cap ?o1) (base ?o2) (camera_checked ?o1) (camera_checked ?o2))
 :effect       (and (assembled ?o1 ?o2)))

)
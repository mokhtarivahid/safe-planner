(define (domain pickit)

  (:requirements :strips :typing :probabilistic-effects)

  (:types graspable container camera location arm object)

  (:predicates  
                (arm ?o - arm)
                (camera ?o - object)
                (package ?o - object)
                (bin ?o - object)
                (stand ?o - object)
                (product ?o - object)
                (graspable ?o - object)

                (occupied ?o - object)
                (free ?o - object)

                (arm_canreach ?a - arm ?o - object)
                (arm_vacuumed ?a - arm ?o - object)
                (arm_gripped ?a - arm ?o - object)
                (arm_at ?a - arm ?o - object)
                (arm_free ?a - arm)

                (object_in ?o - object ?c - object)
                (ungripped ?o - object)
                (upward ?o - object)
                (downward ?o - object)
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

(:action carry_to_stand
 :parameters   (?a - arm ?o ?c ?d - object)
 :precondition (and (arm_vacuumed ?a ?o) (arm_at ?a ?c) (arm_canreach ?a ?d) (stand ?d) (free ?d))
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

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; put/place actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action put_on_stand
 :parameters   (?a - arm ?o ?c - object)
 :precondition (and (arm_vacuumed ?a ?o) (arm_at ?a ?c) (upward ?o) (product ?o) (stand ?c))
 :effect       (and (arm_free ?a) (object_in ?o ?c) (not (arm_vacuumed ?a ?o))))

(:action put_in_pack
 :parameters   (?a - arm ?o ?c - object)
 :precondition (and (arm_gripped ?a ?o) (arm_at ?a ?c) (package ?c) (upward ?o))
 :effect       (and (arm_free ?a) (object_in ?o ?c) (not (arm_gripped ?a ?o)) (not (upward ?o))))
 
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; camera actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action check_upward
 :parameters   (?a - arm ?o ?c - object)
 :precondition (and (arm_vacuumed ?a ?o) (arm_at ?a ?c) (camera ?c))
 :effect (and (camera_checked ?o)
              (probabilistic 0.5 (upward ?o))
              (probabilistic 0.5 (downward ?o))))

(:action rotate_object
 :parameters   (?a - arm ?o - object)
 :precondition (and (arm_vacuumed ?a ?o) (camera_checked ?o) (downward ?o))
 :effect       (and (not (downward ?o)) (upward ?o)))

; (:action rotate_object
;  :parameters   (?a - arm ?o - object)
;  :precondition (and (arm_vacuumed ?a ?o) (camera_checked ?o))
;  :effect       (and (when (not (upward ?o))(upward ?o))))

)
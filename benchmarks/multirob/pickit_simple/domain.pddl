(define (domain pickit)

  (:requirements :strips :typing :conditional-effects :probabilistic-effects)

  (:types container assemble - location graspable arm)

  (:predicates  
                (free ?o - location)

                (arm_canreach ?a - arm ?l - location)
                (arm_at ?a - arm ?l - location)
                (arm_holding ?a - arm ?o - graspable)
                (arm_free ?a - arm)

                (object_in ?o - graspable ?c - location)
                (assembled ?o - graspable ?c - graspable)
                (ungripped ?o - graspable)
                (downward ?o - graspable)
                (upward ?o - graspable)
                ; (unknown_orientation ?o - graspable)

                (packed ?o1 - graspable ?o2 - graspable ?c - location)
                )

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; ABB actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; move/carry actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action move_to_grasp
 :parameters   (?a - arm ?s ?d - location ?o - graspable)
 :precondition (and (arm_free ?a) (arm_at ?a ?s) (arm_canreach ?a ?d) (free ?d) (object_in ?o ?d))
 :effect       (and (arm_at ?a ?d) (not (arm_at ?a ?s)) (free ?s) (not (free ?d))))

(:action carry
 :parameters   (?a - arm ?s ?d - location ?o - graspable)
 :precondition (and (arm_holding ?a ?o) (arm_at ?a ?s) (arm_canreach ?a ?d) (free ?d))
 :effect       (and (arm_at ?a ?d) (not (arm_at ?a ?s)) (free ?s) (not (free ?d))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; vacuum/grip actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; (:action grasp
;  :parameters   (?a - arm ?o - graspable ?l - location)
;  :precondition (and (arm_free ?a) (arm_at ?a ?l) (object_in ?o ?l) (unknown_orientation ?o))
;  :effect       (and (arm_holding ?a ?o) (not (arm_free ?a)) (not (object_in ?o ?l))
;                     (oneof (and (downward ?o) (not (unknown_orientation ?o)))
;                            (and (upward ?o) (not (unknown_orientation ?o))))))

(:action grasp
 :parameters   (?a - arm ?o - graspable ?l - location)
 :precondition (and (arm_free ?a) (arm_at ?a ?l) (object_in ?o ?l))
 :effect       (and (arm_holding ?a ?o) (not (arm_free ?a)) (not (object_in ?o ?l))
                    (oneof (downward ?o)(upward ?o))))

(:action ungrip
 :parameters   (?a - arm ?o - graspable)
 :precondition (and (arm_holding ?a ?o))
 :effect       (and (arm_free ?a) (ungripped ?o) (not (arm_holding ?a ?o))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; put/place actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action put_in_pack
 :parameters   (?a - arm ?o1 ?o2 - graspable ?s - location)
 :precondition (and (assembled ?o1 ?o2) (arm_holding ?a ?o1) (arm_at ?a ?s) (ungripped ?o2))
 :effect       (and (packed ?o1 ?o2 ?s) (arm_free ?a) (not (arm_holding ?a ?o1))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; rotate actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action rotate
 :parameters   (?a - arm ?o - graspable)
 :precondition (and (arm_holding ?a ?o) (upward ?o))
 :effect (and (not (upward ?o)) (downward ?o)))

; (:action rotate
;  :parameters   (?a - arm ?o - graspable)
;  :precondition (and (arm_holding ?a ?o))
;  :effect (and (when (downward ?o) (and (not (downward ?o)) (upward ?o)))
;               (when (upward ?o) (and (not (upward ?o)) (downward ?o)))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; assemble actions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(:action assemble
 :parameters   (?a1 ?a2 - arm ?o1 ?o2 - graspable ?l1 ?l2 - assemble)
 :precondition (and (arm_holding ?a1 ?o1) (arm_at ?a1 ?l1) (downward ?o1) (downward ?o2)
                    (arm_holding ?a2 ?o2) (arm_at ?a2 ?l2))
 :effect       (and (assembled ?o1 ?o2)))

)
(define (domain pickit)

  (:requirements :strips :typing)

  (:types standby container assembly - location arm graspable)

  (:predicates
        (free ?o - location)
        (arm_canreach ?a - arm ?l - location)
        (arm_at ?a - arm ?l - location)
        (arm_grasped ?a - arm ?o - graspable)
        (arm_free ?a - arm)
        (object_in ?o - graspable ?c - container)
        (ungrasped ?o - graspable)
        (disassembled ?o - graspable)
        (assembled ?o - graspable ?c - graspable)
        (packed ?o1 - graspable ?o2 - graspable ?c - container))

  (:action move
   :parameters (?a - arm ?s - location ?d - container ?o - graspable)
   :precondition (and (arm_free ?a)(arm_at ?a ?s)(arm_canreach ?a ?d)(free ?d)(object_in ?o ?d))
   :effect (and (arm_at ?a ?d)(not (arm_at ?a ?s))(free ?s)(not (free ?d))))

  (:action grasp
   :parameters (?a - arm ?o - graspable ?l - container)
   :precondition (and (arm_free ?a)(arm_at ?a ?l)(object_in ?o ?l)(disassembled ?o))
   :effect (and (arm_grasped ?a ?o)(not (arm_free ?a))(not (object_in ?o ?l))))

  (:action ungrasp
   :parameters (?a - arm ?o - graspable)
   :precondition (and (arm_grasped ?a ?o))
   :effect (and (arm_free ?a)(ungrasped ?o)(not (arm_grasped ?a ?o))))

  (:action carry
   :parameters (?a - arm ?o - graspable ?s - location ?d - location)
   :precondition (and (arm_grasped ?a ?o)(disassembled ?o)(arm_at ?a ?s)(arm_canreach ?a ?d)(free ?d))
   :effect (and (arm_at ?a ?d)(not (arm_at ?a ?s))(free ?s)(not (free ?d))))

  (:action carry
   :parameters (?a - arm ?o1 - graspable ?o2 - graspable ?s - location ?d - location)
   :precondition (and (assembled ?o1 ?o2)(arm_grasped ?a ?o1)(ungrasped ?o2)(arm_at ?a ?s)(arm_canreach ?a ?d)(free ?d))
   :effect (and (arm_at ?a ?d)(not (arm_at ?a ?s))(free ?s)(not (free ?d))))

  (:action pack
   :parameters (?a - arm ?o1 - graspable ?o2 - graspable ?s - container)
   :precondition (and (assembled ?o1 ?o2)(arm_grasped ?a ?o1)(arm_at ?a ?s)(ungrasped ?o2))
   :effect (and (packed ?o1 ?o2 ?s)(arm_free ?a)(not (arm_grasped ?a ?o1))(not (ungrasped ?o2))))

  (:action assemble
   :parameters (?a1 - arm ?a2 - arm ?o1 - graspable ?o2 - graspable ?l1 - assembly ?l2 - assembly)
   :precondition (and (arm_grasped ?a1 ?o1)(arm_at ?a1 ?l1)(arm_grasped ?a2 ?o2)(arm_at ?a2 ?l2)(disassembled ?o1)(disassembled ?o2))
   :effect (and (assembled ?o1 ?o2)(not (disassembled ?o1))(not (disassembled ?o2))))
)

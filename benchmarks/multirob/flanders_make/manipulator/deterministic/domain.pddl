(define (domain manipulator)
  (:requirements :strips :typing)

  (:types shelf slot - container
          platform
          gripper
          location
          object
          type)

  (:predicates
      ;; location
      (can_move ?p - platform ?l - location)
      (has_shelf ?l - location ?c - container)

      ;; platform
      (platform_at ?p - platform ?l - location)
      (has_gripper ?p - platform ?g - gripper)
      (has_slot ?p - platform ?c - container)

      ;; gripper
      (gripper_at_platform ?g - gripper)
      (gripper_at ?g - gripper ?c - container)
      (gripper_holding ?g - gripper ?o - object)
      (gripper_free ?g - gripper)

      ;; object
      (object_type ?o - object ?t - type)
      (object_at ?o - object ?c - container)
      (object_type_at ?t - type ?c - container)
  )

  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  ;; ACTIONS
  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

  (:action move_platform
      :parameters   (?p - platform ?g - gripper ?s - location ?d - location)
      :precondition (and (platform_at ?p ?s) (can_move ?p ?d) (gripper_at_platform ?g))
      :effect       (and (not (platform_at ?p ?s)) (platform_at ?p ?d)))


  (:action move_gripper_to_shelf
      :parameters   (?p - platform ?g - gripper ?s - container ?d - container ?l - location)
      :precondition (and (platform_at ?p ?l) (has_gripper ?p ?g) (gripper_at ?g ?s) (has_shelf ?l ?d))
      :effect       (and (not (gripper_at ?g ?s)) (gripper_at ?g ?d) (not (gripper_at_platform ?g))))


  (:action move_gripper_to_slot
      :parameters   (?p - platform ?g - gripper ?s - container ?d - container)
      :precondition (and (has_gripper ?p ?g) (gripper_at ?g ?s) (has_slot ?p ?d))
      :effect       (and (not (gripper_at ?g ?s)) (gripper_at ?g ?d) (gripper_at_platform ?g)))


  (:action pickup_from_shelf
      :parameters   (?p - platform ?g - gripper ?o - object ?c - container ?l - location)
      :precondition (and (platform_at ?p ?l) (has_shelf ?l ?c) (object_at ?o ?c) (gripper_at ?g ?c) (gripper_free ?g))
      :effect       (and (not (gripper_free ?g)) (not (object_at ?o ?c)) (gripper_holding ?g ?o)))


  (:action put_object
      :parameters   (?p - platform ?g - gripper ?o - object ?t - type ?c - container)
      :precondition (and (has_gripper ?p ?g) (has_slot ?p ?c) (gripper_at ?g ?c) (gripper_holding ?g ?o) (object_type ?o ?t))
      :effect       (and (not (gripper_holding ?g ?o)) (gripper_free ?g) (object_at ?o ?c) (object_type_at ?t ?c)))
)

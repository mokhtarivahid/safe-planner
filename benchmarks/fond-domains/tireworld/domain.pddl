;;;  Authors: Michael Littman and David Weissman  ;;;
;;;  Modified: Blai Bonet for IPC 2006 ;;;

(define (domain tire)
  (:requirements :typing :strips :equality :non-deterministic)
  (:types location)
  (:predicates (vehicle-at ?loc - location) (spare-in ?loc - location) (road ?from - location ?to - location) (not-flattire) (hasspare))
  (:action move-car
    :parameters (?from - location ?to - location)
    :precondition (and (vehicle-at ?from) (road ?from ?to) (not-flattire))
    :effect (and (vehicle-at ?to) (not (vehicle-at ?from)) (oneof (and) (not (not-flattire))))
  )
  (:action loadtire
    :parameters (?loc - location)
    :precondition (and (vehicle-at ?loc) (spare-in ?loc))
    :effect (and (hasspare) (not (spare-in ?loc)))
  )
  (:action changetire
    :precondition (hasspare)
    :effect (oneof (and) (and (not (hasspare)) (not-flattire)))
  )
)


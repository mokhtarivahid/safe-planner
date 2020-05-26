(define (domain gripper-strips)
(:requirements :strips :typing :probabilistic-effects) 
(:types room object robot gripper)
(:predicates 
    (at-robby ?r - robot ?x - room)
    (at ?o - object ?x - room)
    (free ?r - robot ?g - gripper)
    (carry ?r - robot ?o - object ?g - gripper)
    (low-charge ?r - robot)
    (has-charge ?r - robot)
    )

(:action move
  :parameters (?r - robot ?from ?to - room)
  :precondition (and (at-robby ?r ?from) (has-charge ?r))
  :effect (and (at-robby ?r ?to) (not (at-robby ?r ?from))
               (probabilistic 
                    0.1 (and (low-charge ?r) (not (has-charge ?r))))))

(:action pick
  :parameters (?r - robot ?obj - object ?room - room ?g - gripper)
  :precondition (and (at ?obj ?room) (at-robby ?r ?room) (free ?r ?g) (has-charge ?r))
  :effect (and (carry ?r ?obj ?g) (not (at ?obj ?room)) (not (free ?r ?g))))

(:action drop
  :parameters (?r - robot ?obj - object ?room - room ?g - gripper)
  :precondition (and (carry ?r ?obj ?g) (at-robby ?r ?room) (has-charge ?r))
  :effect (and (at ?obj ?room) (free ?r ?g) (not (carry ?r ?obj ?g))))

(:action charge
  :parameters (?r - robot ?l - room)
  :precondition (and (low-charge ?r) (at-robby ?r ?l))
  :effect (and (has-charge ?r) (not (low-charge ?r))))
)
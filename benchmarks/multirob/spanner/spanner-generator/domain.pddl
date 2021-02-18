(define (domain spanner)

(:requirements :typing :strips :probabilistic-effects)

(:types robot serviceman - agent
        agent nut spanner - locatable 
        toolbox - location)

(:predicates 
  (link ?l1 - location ?l2 - location)
  (at ?r - locatable ?l - location)
  (free ?r - robot)
  (carrying ?r - robot ?s - spanner)
  (useable ?s - spanner)
  (broken ?s - spanner)
  (size ?n - nut ?s - spanner)
  (tightened ?n - nut)
  (loose ?n - nut))

(:action move
  :parameters (?r - robot ?s - location ?d - location)
  :precondition (and (at ?r ?s) (link ?s ?d))
  :effect (and (not (at ?r ?s)) (at ?r ?d)))

(:action take_spanner
  :parameters (?r - robot ?s - spanner ?l - toolbox)
  :precondition (and (at ?r ?l) (at ?s ?l) (free ?r))
  :effect (and (carrying ?r ?s) (not (free ?r)) (not (at ?s ?l))))

(:action put_spanner
  :parameters (?r - robot ?s - spanner ?l - toolbox)
  :precondition (and (at ?r ?l) (carrying ?r ?s))
  :effect (and (at ?s ?l) (not (carrying ?r ?s)) (free ?r)))

(:action screw_nut
  :parameters (?r - robot ?s - spanner ?n - nut ?l - location)
  :precondition (and (at ?r ?l) (at ?n ?l) (carrying ?r ?s) (size ?n ?s) (useable ?s) (loose ?n))
  :effect (oneof (and (not (loose ?n)) (tightened ?n) (broken ?s) (not (useable ?s)))
                 (and (broken ?s) (not (useable ?s)))
                 (and (not (loose ?n)) (tightened ?n))))

(:action fix_spanner
  :parameters (?r - robot ?s - spanner ?m - serviceman ?l - location)
  :precondition (and (at ?r ?l) (at ?m ?l) (carrying ?r ?s) (broken ?s))
  :effect (and (useable ?s) (not (broken ?s))))

)

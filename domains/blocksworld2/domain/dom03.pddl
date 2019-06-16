(define (domain blocks-domain)
  (:requirements :equality :typing)
  (:types block)
  (:predicates (holding ?b - block) (emptyhand) (on-table ?b - block) (on ?b1 ?b2 - block) (clear ?b - block))

  (:action pick-up
    :parameters (?b1 ?b2 - block)
    :precondition (and (not (= ?b1 ?b2)) (emptyhand) (clear ?b1) (on ?b1 ?b2))
    :effect (and (holding ?b1) (clear ?b2) (not (emptyhand)) (not (clear ?b1)) (not (on ?b1 ?b2)))
  )

  (:action pick-up-from-table
    :parameters (?b - block)
    :precondition (and (emptyhand) (clear ?b) (on-table ?b))
    :effect (and (emptyhand) (clear ?b) (on-table ?b))
  )

  (:action put-on-block
    :parameters (?b1 ?b2 - block)
    :precondition (and (holding ?b1) (clear ?b2))
    :effect (and (on ?b1 ?b2) (emptyhand) (clear ?b1) (not (holding ?b1)) (not (clear ?b2)))
  )

  (:action put-down
    :parameters (?b - block)
    :precondition (holding ?b)
    :effect (and (on-table ?b) (emptyhand) (clear ?b) (not (holding ?b)))
  )

  (:action pick-tower
    :parameters (?b1 ?b2 ?b3 - block)
    :precondition (and (emptyhand) (on ?b1 ?b2) (on ?b2 ?b3))
    :effect (and (holding ?b2) (clear ?b3) (not (emptyhand)) (not (on ?b2 ?b3)))
  )

  (:action put-tower-on-block
    :parameters (?b1 ?b2 ?b3 - block)
    :precondition (and (holding ?b2) (on ?b1 ?b2) (clear ?b3))
    :effect (and (on-table ?b2) (emptyhand) (not (holding ?b2)))
  )

  (:action put-tower-down
    :parameters (?b1 ?b2 - block)
    :precondition (and (holding ?b2) (on ?b1 ?b2))
    :effect (and (on-table ?b2) (emptyhand) (not (holding ?b2)))
  )
)

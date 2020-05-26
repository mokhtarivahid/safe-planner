(define (domain blocks-domain)
  (:requirements :equality :typing)
  (:types block)
  (:predicates (holding ?b - block) (emptyhand) (on-table ?b - block) (on ?b1 ?b2 - block) (clear ?b - block))
  (:action pick-up1
    :parameters (?b1 ?b2 - block)
    :precondition (and (not (= ?b1 ?b2)) (emptyhand) (clear ?b1) (on ?b1 ?b2))
    :effect
        (and (holding ?b1) (clear ?b2) (not (emptyhand)) (not (clear ?b1)) (not (on ?b1 ?b2)))
  )
  (:action pick-up2
    :parameters (?b1 ?b2 - block)
    :precondition (and (not (= ?b1 ?b2)) (emptyhand) (clear ?b1) (on ?b1 ?b2))
    :effect
        (and (clear ?b2) (on-table ?b1) (not (on ?b1 ?b2)))
  )
  (:action pick-up-from-table1
    :parameters (?b - block)
    :precondition (and (emptyhand) (clear ?b) (on-table ?b))
    :effect (and (holding ?b) (not (emptyhand)) (not (on-table ?b)))
  )
  (:action pick-up-from-table2
    :parameters (?b - block)
    :precondition (and (emptyhand) (clear ?b) (on-table ?b))
    :effect (and (emptyhand) (clear ?b) (on-table ?b))
  )
  (:action put-on-block1
    :parameters (?b1 ?b2 - block)
    :precondition (and (holding ?b1) (clear ?b2))
    :effect (and (on ?b1 ?b2) (emptyhand) (clear ?b1) (not (holding ?b1)) (not (clear ?b2)))
  )
  (:action put-on-block2
    :parameters (?b1 ?b2 - block)
    :precondition (and (holding ?b1) (clear ?b2))
    :effect (and (on-table ?b1) (emptyhand) (clear ?b1) (not (holding ?b1)))
  )
  (:action put-down
    :parameters (?b - block)
    :precondition (holding ?b)
    :effect (and (on-table ?b) (emptyhand) (clear ?b) (not (holding ?b)))
  )
  (:action pick-tower1
    :parameters (?b1 ?b2 ?b3 - block)
    :precondition (and (emptyhand) (on ?b1 ?b2) (on ?b2 ?b3))
    :effect
      (and (holding ?b2) (clear ?b3) (not (emptyhand)) (not (on ?b2 ?b3)))
  )
  (:action pick-tower2
    :parameters (?b1 ?b2 ?b3 - block)
    :precondition (and (emptyhand) (on ?b1 ?b2) (on ?b2 ?b3))
    :effect (and (emptyhand) (on ?b1 ?b2) (on ?b2 ?b3))
  )
  (:action put-tower-on-block1
    :parameters (?b1 ?b2 ?b3 - block)
    :precondition (and (holding ?b2) (on ?b1 ?b2) (clear ?b3))
    :effect (and (on ?b2 ?b3) (emptyhand) (not (holding ?b2)) (not (clear ?b3)))
  )
  (:action put-tower-on-block2
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

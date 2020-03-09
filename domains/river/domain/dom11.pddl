(define (domain river)
  (:requirements :typing :strips)
  (:predicates (on-near-bank) (on-far-bank) (on-island) (alive))

  (:action traverse-rocks :parameters ()
     :precondition (and (on-near-bank))
     :effect (and (not (on-near-bank))(on-far-bank)))

  (:action swim-river :parameters ()
     :precondition (and (on-near-bank))
     :effect (and (not (on-near-bank))(on-far-bank)))

  (:action swim-island :parameters ()
     :precondition (and (on-island))
     :effect (and (not (on-island))(not (alive))))
)

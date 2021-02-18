(define (domain test)

  (:requirements :typing :non-deterministic)

  (:types fact)

  (:predicates
    (x-true)
    (y-true)
    (x-false)
    (y-false)
  ) 

  (:action change
    :parameters ()
    :effect (oneof 
          (and (x-true) (not (x-false)))
          (and (y-true) (not (y-false)))
          ))

)

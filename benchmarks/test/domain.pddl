(define (domain test)

  (:requirements :typing :non-deterministic)

  (:types fact)

  (:predicates
    (true ?x - fact)
    (false ?x - fact)
  ) 

  (:action change
    :parameters (?x - fact ?y - fact)
    :effect (oneof 
    	(and (true ?x)(not(false ?x)))
    	(and (true ?y)(not(false ?y)))
    	))

)

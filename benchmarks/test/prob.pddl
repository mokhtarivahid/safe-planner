(define (problem prob1)
	
  (:domain test)

  (:objects x y - fact)

  (:init
    (false x)
    (false y)
  ) 

  (:goal
  	(and (true x) (true y))
  ))
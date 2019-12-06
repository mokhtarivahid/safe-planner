(define (problem prob1)
(:domain tabletop)
(:objects 
          left-arm right-arm - arm
          obj1 obj2 obj3 obj4 - object)

(:init 
          (free left-arm)
          (free right-arm)

          (reachable left-arm obj1)
          (reachable left-arm obj2)
          (reachable left-arm obj3)
          (reachable left-arm obj4)

          (reachable right-arm obj1)
          (reachable right-arm obj2)
          (reachable right-arm obj3)
          (reachable right-arm obj4)

          (unobstructed obj1 obj2)
          (unobstructed obj1 obj3)
          (unobstructed obj1 obj4)
          )

(:goal  (and
          (holding obj1)
        ))
)
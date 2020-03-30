(define (problem prob1)
(:domain pullandpick)
(:objects 
          left-arm right-arm - arm
          object1 object2 - graspable)

(:init 
          (free left-arm)
          (free right-arm)

          (ontable object1)
          (ontable object2)

          (ungrasped object1)
          (ungrasped object2)

          (reachable left-arm object1)
          (reachable left-arm object2)

          (reachable right-arm object1)
          (reachable right-arm object2)

          ;;;;;;;;;;;;;;;;;;;;;;;;;;
          ;; constraint 1
          ; (unobstructed object1)
          (unobstructed object2)

          (obstructed object1 object2)

          ;;;;;;;;;;;;;;;;;;;;;;;;;;
          ;; constraint 2
          (nearby object1 left-arm)
          (nearby object1 right-arm)
          (nearby object2 left-arm)
          (nearby object2 right-arm)

          ; (heavy object1 left-arm)
          ; (heavy object1 right-arm)
          ; (heavy object2 left-arm)
          ; (heavy object2 right-arm)
          )

(:goal  (and
          (lifted object1)
        ))
)
(define (problem prob2)
(:domain pullandpick)
(:objects 
          left-arm right-arm - arm
          object1 object2 object3 - graspable)

(:init 
          (free left-arm)
          (free right-arm)

          (ontable object1)
          (ontable object2)
          (ontable object3)

          (ungrasped object1)
          (ungrasped object2)
          (ungrasped object3)

          (reachable left-arm object1)
          (reachable left-arm object2)
          (reachable left-arm object3)

          (reachable right-arm object1)
          (reachable right-arm object2)
          (reachable right-arm object3)

          ;;;;;;;;;;;;;;;;;;;;;;;;;;
          ;; constraint 1 when an arm obstructs another object
          ; (grasped left-arm object2)
          ; (obstructed object1 left-arm)

          ;;;;;;;;;;;;;;;;;;;;;;;;;;
          ;; constraint 2
          ; (unobstructed object1)
          ; (unobstructed object2)
          (unobstructed object3)

          (obstructed object1 object2)
          (obstructed object2 object3)

          ;;;;;;;;;;;;;;;;;;;;;;;;;;
          ;; constraint 3
          (nearby object1 left-arm)
          (nearby object1 right-arm)
          (nearby object2 left-arm)
          (nearby object2 right-arm)
          (nearby object3 left-arm)
          (nearby object3 right-arm)

          ; (heavy object1 left-arm)
          ; (heavy object1 right-arm)
          ; (heavy object2 left-arm)
          ; (heavy object2 right-arm)
          )

(:goal  (and
          (lifted object1)
          ; (lifted object2)
        ))
)
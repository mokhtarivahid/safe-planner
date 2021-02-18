(define (problem prob1)
(:domain pullandpick)
(:objects 
          left_arm right_arm - arm
          object1 object2 - graspable)

(:init 
          (free left_arm)
          (free right_arm)

          (ontable object1)
          (ontable object2)

          (ungrasped object1)
          (ungrasped object2)

          (reachable left_arm object1)
          (reachable left_arm object2)

          (reachable right_arm object1)
          (reachable right_arm object2)

          ;;;;;;;;;;;;;;;;;;;;;;;;;;
          ;; constraint 1
          (unobstructed object1)
          (unobstructed object2)

          ; (obstructed object1 object2)

          ;;;;;;;;;;;;;;;;;;;;;;;;;;
          ;; constraint 2
          (nearby object1 left_arm)
          (nearby object1 right_arm)
          (nearby object2 left_arm)
          (nearby object2 right_arm)

          ; (heavy object1 left_arm)
          ; (heavy object1 right_arm)
          ; (heavy object2 left_arm)
          ; (heavy object2 right_arm)
          )

(:goal  (and
          (lifted object1)
        ))
)
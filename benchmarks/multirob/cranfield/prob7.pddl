;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Cranfield assembly domain
;; Planners supporting derived-predicates: FF-X, LPG-TD, FD using additive heuristic
;; initial state: all objects are initially assembled in the faceplate_top
;; goal: replace old items, e.g., shaft, with new ones, e.g., shaft2, 
;;       in an already assembled cranfield on faceplate_top
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(define (problem replace_assemble_faceplate_top)

  (:domain cranfield)

  (:objects 
            arm_left arm_right - robot
            arm_left_home_pos arm_right_home_pos - robot_pos

            table - table

            faceplate_top faceplate_bottom - faceplate

            square_peg_left square_peg_right - square_peg
            round_peg_left round_peg_right - round_peg
            shaft - shaft
            pendulum - pendulum
            spacer - spacer

            square_peg_home_pos_left square_peg_home_pos_right - square_peg_pos
            round_peg_home_pos_left round_peg_home_pos_right - round_peg_pos
            shaft_home_pos - shaft_pos
            pendulum_home_pos - pendulum_pos
            spacer_home_pos - spacer_pos

            ; target position on top faceplate
            square_peg_pos_left square_peg_pos_right - square_peg_pos
            round_peg_pos_left round_peg_pos_right - round_peg_pos
            shaft_pos - shaft_pos 
            pendulum_pos - pendulum_pos 
            spacer_pos - spacer_pos

            ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
            ; extra objects
            square_peg_left2 square_peg_right2 - square_peg
            round_peg_left2 round_peg_right2 - round_peg
            shaft2 - shaft
            pendulum2 - pendulum
            spacer2 - spacer

            ; extra objects home position on the table
            square_peg_home_pos_left2 square_peg_home_pos_right2 - square_peg_pos
            round_peg_home_pos_left2 round_peg_home_pos_right2 - round_peg_pos
            shaft_home_pos2 - shaft_pos
            pendulum_home_pos2 - pendulum_pos
            spacer_home_pos2 - spacer_pos

            )

  (:init 
            ; arm initial position
            (robot_at arm_left arm_left_home_pos table)
            (robot_at arm_right arm_right_home_pos table)

            ; arm hand is empty
            (arm_free arm_left)
            ; (arm_free arm_right)

            ; objects initial locations
            (object_at pendulum pendulum_pos faceplate_top)
            (object_at spacer spacer_pos faceplate_top)
            (object_at shaft shaft_pos faceplate_top)
            (object_at square_peg_left square_peg_pos_left faceplate_top)
            (object_at square_peg_right square_peg_pos_right faceplate_top)
            (object_at round_peg_left round_peg_pos_left faceplate_top)
            (object_at round_peg_right round_peg_pos_right faceplate_top)

            ; objects initial locations
            (inserted pendulum faceplate_top)
            (inserted spacer faceplate_top)
            (inserted shaft faceplate_top)
            (inserted square_peg_left faceplate_top)
            (inserted square_peg_right faceplate_top)
            (inserted round_peg_left faceplate_top)
            (inserted round_peg_right faceplate_top)

            ; objects are empty to reach
            (reachable pendulum)
            (reachable spacer)
            (reachable shaft)
            (reachable square_peg_left)
            (reachable square_peg_right)
            (reachable round_peg_left)
            (reachable round_peg_right)

            ; home positions are empty to reach
            (reachable shaft_home_pos)
            (reachable square_peg_home_pos_left)
            (reachable square_peg_home_pos_right)
            (reachable round_peg_home_pos_left)
            (reachable round_peg_home_pos_right)
            (reachable pendulum_home_pos)
            (reachable spacer_home_pos)

            ; positions are empty to reach
            (reachable shaft_pos)
            (reachable square_peg_pos_left)
            (reachable square_peg_pos_right)
            (reachable round_peg_pos_left)
            (reachable round_peg_pos_right)
            (reachable pendulum_pos)
            (reachable spacer_pos)

            ; positions are empty to insert
            (empty shaft_home_pos table)
            (empty square_peg_home_pos_left table)
            (empty square_peg_home_pos_right table)
            (empty round_peg_home_pos_left table)
            (empty round_peg_home_pos_right table)
            (empty pendulum_home_pos table)
            (empty spacer_home_pos table)

            ; positions are empty to insert
            (empty shaft_pos faceplate_bottom)
            (empty square_peg_pos_left faceplate_bottom)
            (empty square_peg_pos_right faceplate_bottom)
            (empty round_peg_pos_left faceplate_bottom)
            (empty round_peg_pos_right faceplate_bottom)
            (empty pendulum_pos faceplate_bottom)
            (empty spacer_pos faceplate_bottom)

            ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
            ; extra objects initial locations
            (object_at shaft2 shaft_home_pos2 table)
            (object_at square_peg_left2 square_peg_home_pos_left2 table)
            (object_at square_peg_right2 square_peg_home_pos_right2 table)
            (object_at round_peg_left2 round_peg_home_pos_left2 table)
            (object_at round_peg_right2 round_peg_home_pos_right2 table)
            (object_at pendulum2 pendulum_home_pos2 table)
            (object_at spacer2 spacer_home_pos2 table)

            ; extra objects are empty to reach
            (reachable shaft2)
            (reachable square_peg_left2)
            (reachable square_peg_right2)
            (reachable round_peg_left2)
            (reachable round_peg_right2)
            (reachable pendulum2)
            (reachable spacer2)

            ; extra objects home positions are empty to reach
            (reachable shaft_home_pos2)
            (reachable square_peg_home_pos_left2)
            (reachable square_peg_home_pos_right2)
            (reachable round_peg_home_pos_left2)
            (reachable round_peg_home_pos_right2)
            (reachable pendulum_home_pos2)
            (reachable spacer_home_pos2)

            )

  (:goal (and
            (cranfield_assembled faceplate_top)
            ; (object_at pendulum2 pendulum_pos faceplate_top)
            ; (inserted pendulum2 faceplate_top)
            (object_at shaft2 shaft_pos faceplate_top)
            (inserted shaft2 faceplate_top)
            ; (object_at spacer2 spacer_pos faceplate_top)
            ; (inserted spacer2 faceplate_top)
            ; (object_at round_peg_left2 round_peg_pos_left faceplate_top)
            ; (object_at round_peg_right2 round_peg_pos_right faceplate_top)
            ; (inserted round_peg_left2 faceplate_top)
            ; (inserted round_peg_right2 faceplate_top)
          ))
)
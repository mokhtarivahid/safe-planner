;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Cranfield assembly domain
;; Planners supporting derived-predicates: FF-X, LPG-TD, FD using additive heuristic
;; initial state: all objects are initially on the table
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(define (problem assemble_table_to_faceplate_top)

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

            ; home position on the table
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

            )

  (:init 
            ; arm initial position
            (robot_at arm_left arm_left_home_pos table)
            (robot_at arm_right arm_right_home_pos table)

            ; arm hand is empty
            (arm_free arm_left)
            ; (arm_free arm_right)

            ; objects initial locations
            (object_at pendulum pendulum_home_pos table)
            (object_at spacer spacer_home_pos table)
            (object_at shaft shaft_home_pos table)
            (object_at square_peg_left square_peg_home_pos_left table)
            (object_at square_peg_right square_peg_home_pos_right table)
            (object_at round_peg_left round_peg_home_pos_left table)
            (object_at round_peg_right round_peg_home_pos_right table)

            ; objects are empty to reach
            (reachable pendulum)
            (reachable spacer)
            (reachable shaft)
            (reachable square_peg_left)
            (reachable square_peg_right)
            (reachable round_peg_left)
            (reachable round_peg_right)

            ; positions are empty to reach
            (reachable shaft_pos)
            (reachable square_peg_pos_left)
            (reachable square_peg_pos_right)
            (reachable round_peg_pos_left)
            (reachable round_peg_pos_right)
            (reachable pendulum_pos)
            (reachable spacer_pos)

            ; positions are empty to insert
            (empty shaft_pos faceplate_top)
            (empty square_peg_pos_left faceplate_top)
            (empty square_peg_pos_right faceplate_top)
            (empty round_peg_pos_left faceplate_top)
            (empty round_peg_pos_right faceplate_top)
            (empty pendulum_pos faceplate_top)
            (empty spacer_pos faceplate_top)

            ; positions are empty to insert
            (empty shaft_pos faceplate_bottom)
            (empty square_peg_pos_left faceplate_bottom)
            (empty square_peg_pos_right faceplate_bottom)
            (empty round_peg_pos_left faceplate_bottom)
            (empty round_peg_pos_right faceplate_bottom)
            (empty pendulum_pos faceplate_bottom)
            (empty spacer_pos faceplate_bottom)
            )

  (:goal (and
            (cranfield_assembled faceplate_top)
          ))
)
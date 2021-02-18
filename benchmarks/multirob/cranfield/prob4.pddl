;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Cranfield assembly domain
;; Planners supporting derived-predicates: FF-X, LPG-TD, FD (additive heuristic)
;; initial state: all objects are initially assembled in the faceplate_top
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(define (problem assemble_faceplate_top_to_faceplate_bottom)

  (:domain cranfield)

  (:objects 
            arm_left arm_right - robot
            arm_left_home_pos arm_right_home_pos - robot_pos

            table - table

            faceplate_top faceplate_bottom - faceplate

            square_peg_left square_peg_right - square_peg
            round_peg_left round_peg_right - round_peg
            shaft - shaft
            lever - lever
            spacer - spacer

            ; home position on the table
            square_peg_home_pos_left square_peg_home_pos_right - square_peg_pos
            round_peg_home_pos_left round_peg_home_pos_right - round_peg_pos
            shaft_home_pos - shaft_pos
            lever_home_pos - lever_pos
            spacer_home_pos - spacer_pos

            ; target position on top faceplate
            square_peg_pos_left square_peg_pos_right - square_peg_pos
            round_peg_pos_left round_peg_pos_right - round_peg_pos
            shaft_pos - shaft_pos 
            lever_pos - lever_pos 
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
            (object_at lever lever_pos faceplate_top)
            (object_at spacer spacer_pos faceplate_top)
            (object_at shaft shaft_pos faceplate_top)
            (object_at square_peg_left square_peg_pos_left faceplate_top)
            (object_at square_peg_right square_peg_pos_right faceplate_top)
            (object_at round_peg_left round_peg_pos_left faceplate_top)
            (object_at round_peg_right round_peg_pos_right faceplate_top)

            ; objects are empty to reach
            (reachable lever)
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
            (reachable shaft_home_pos)
            (reachable lever_home_pos)
            (reachable spacer_home_pos)

            ; positions are empty to reach
            (reachable shaft_pos)
            (reachable square_peg_pos_left)
            (reachable square_peg_pos_right)
            (reachable round_peg_pos_left)
            (reachable round_peg_pos_right)
            (reachable shaft_pos)
            (reachable lever_pos)
            (reachable spacer_pos)

            ; positions are empty to insert
            (empty shaft_home_pos table)
            (empty square_peg_home_pos_left table)
            (empty square_peg_home_pos_right table)
            (empty round_peg_home_pos_left table)
            (empty round_peg_home_pos_right table)
            (empty shaft_home_pos table)
            (empty lever_home_pos table)
            (empty spacer_home_pos table)

            ; positions are empty to insert
            (empty shaft_pos faceplate_bottom)
            (empty square_peg_pos_left faceplate_bottom)
            (empty square_peg_pos_right faceplate_bottom)
            (empty round_peg_pos_left faceplate_bottom)
            (empty round_peg_pos_right faceplate_bottom)
            (empty shaft_pos faceplate_bottom)
            (empty lever_pos faceplate_bottom)
            (empty spacer_pos faceplate_bottom)
            )

  (:goal (and
            ; (cranfield_assembled faceplate_bottom)
            (cranfield_disassembled faceplate_top)
          ))
)
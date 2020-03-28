(define (problem prob1)

(:domain solenoid)

(:objects s1 - solenoid
          h1 - hole)

(:init

    (unknown (on s1 h1))
    (unknown (removed s1))
    (oneof (on s1 h1) (removed s1))

    (unknown (human_at s1))
    (unknown (no_human_at s1))
    (oneof (human_at s1) (no_human_at s1))

    (robot_at_table)
    (gripper_free))

(:goal 
    (and
        (removed s1)))
)

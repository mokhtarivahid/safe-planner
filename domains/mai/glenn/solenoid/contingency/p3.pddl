(define (problem prob1)

(:domain solenoid)

(:objects s1 s2 s3 - solenoid
          h1 h2 h3 - hole)

(:init

    (unknown (on s1 h1))
    (unknown (removed s1))
    (oneof (on s1 h1) (removed s1))

    (unknown (on s2 h2))
    (unknown (removed s2))
    (oneof (on s2 h2) (removed s2))

    (unknown (on s3 h3))
    (unknown (removed s3))
    (oneof (on s3 h3) (removed s3))

    (unknown (human_at s1))
    (unknown (no_human_at s1))
    (oneof (human_at s1) (no_human_at s1))

    (unknown (no_human_at s2))
    (unknown (human_at s2))
    (oneof (human_at s2) (no_human_at s2))

    (unknown (no_human_at s3))
    (unknown (human_at s3))
    (oneof (human_at s3) (no_human_at s3))

    (robot_at_table)
    (gripper_free))

(:goal 
    (and
        (removed s1)
        (removed s2)))
)

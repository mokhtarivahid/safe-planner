(define (domain solenoid)
(:types solenoid hole)
(:predicates (on ?x - solenoid ?y - hole)
             (holding ?x - solenoid)
             (robot_at ?h - hole)
             (human_at ?x - solenoid)
             (no_human_at ?x - solenoid)
             (removed ?s - solenoid)
             (ontable ?s - solenoid)
             (gripper_free)
             (robot_at_table)
             )

(:action senseON
 :parameters (?s - solenoid ?h - hole)
 :observe (on ?s ?h))

(:action move
  :parameters (?s - solenoid ?h - hole)
  :precondition (and (on ?s ?h)(robot_at_table))
  :effect (and 
          (when (no_human_at ?s)
                (and(robot_at ?h)(not(robot_at_table))))
          (when (human_at ?s)
                (and(removed ?s)(not(on ?s ?h))))))

(:action pickup
  :parameters (?s - solenoid ?h - hole)
  :precondition (and (gripper_free)(robot_at ?h)(on ?s ?h))
  :effect (and (holding ?s)(removed ?s)(not(on ?s ?h))(not(gripper_free))))

(:action carry
  :parameters (?s - solenoid ?h - hole)
  :precondition (and (holding ?s)(robot_at ?h))
  :effect (and (robot_at_table)(not(robot_at ?h))))

(:action putdown
  :parameters (?s - solenoid)
  :precondition (and (holding ?s)(robot_at_table))
  :effect (and (ontable ?s)(gripper_free)(not(holding ?s))))

)

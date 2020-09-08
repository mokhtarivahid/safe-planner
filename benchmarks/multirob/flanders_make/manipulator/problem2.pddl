;;  -------------------------------------------------------
;;  |          RACK_A          |          RACK_B          |
;;  -------------------------------------------------------
;;  | SHELF1 | SHELF2 | SHELF3 | SHELF1 | SHELF2 | SHELF3 |
;;  -------------------------------------------------------
;;  |  OBJ1  |  OBJ2  |  OBJ3  |  OBJ4  |  OBJ5  |  OBJ6  | 
;;  -------------------------------------------------------
;;  |                                                     |
;;  |         PLATFORM                                    |
;;  |      ---------------                                |
;;  |      |SLOT1 | SLOT2|                                |
;;  |      ---------------                                |
;;  |      |SLOT3 | SLOT4|                                |
;;  |      ---------------                                |
;;  |                                                     |


(define (problem prob2)
    (:domain manipulator)
    (:objects
        platform - platform
        gripper - gripper
        rack_A
        rack_B - location
        rack_A_shelve1
        rack_A_shelve2
        rack_A_shelve3 
        rack_B_shelve1
        rack_B_shelve2
        rack_B_shelve3 - shelf
        slot1
        slot2
        slot3
        slot4 - slot
        obj1 
        obj2 
        obj3 
        obj4 
        obj5 
        obj6 - object
        blue_cube 
        blue_cylinder 
        blue_hexagon 
        red_cube 
        red_cylinder 
        red_hexagon 
        green_cube 
        green_cylinder 
        green_hexagon - type
    )
    (:init
        ;; Location initialization
        (can_move platform rack_A)
        (can_move platform rack_B)
        (has_shelf rack_A rack_A_shelve1)
        (has_shelf rack_A rack_A_shelve2)
        (has_shelf rack_A rack_A_shelve3)
        (has_shelf rack_B rack_B_shelve1)
        (has_shelf rack_B rack_B_shelve2)
        (has_shelf rack_B rack_B_shelve3)

        ;; Platform initialization
        (platform_at platform rack_A)
        (has_gripper platform gripper)
        (has_slot platform slot1)
        (has_slot platform slot2)
        (has_slot platform slot3)
        (has_slot platform slot4)

        ;; Gripper initialization
        (gripper_at gripper slot1)
        (gripper_free gripper)
        (gripper_at_platform gripper)

        ;; Object initialization
        ; OBJ1      
        (object_at obj1 rack_A_shelve1)
        (object_type obj1 red_cylinder)
        ; OBJ2
        (object_at obj2 rack_A_shelve2)
        (object_type obj2 green_cylinder)
        ; OBJ3
        (object_at obj3 rack_A_shelve3)
        (object_type obj3 blue_cylinder)
        ; OBJ4
        (object_at obj4 rack_B_shelve1)
        (object_type obj4 red_cube)
        ; OBJ5
        (object_at obj5 rack_B_shelve2)
        (object_type obj5 green_cube)
        ; OBJ6
        (object_at obj6 rack_B_shelve3)
        (object_type obj6 blue_cube)
    )
    (:goal 
      (and
        (object_type_at green_cylinder slot1)
        (object_type_at red_cylinder slot2)
        (object_type_at blue_cube slot3)
        (object_type_at green_cube slot4)
      )
    )
)
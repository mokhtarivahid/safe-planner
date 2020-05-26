(define (problem prob0)
  (:domain pickit)
  (:objects 
		arm1 arm2 - arm
		assembly_pose1 assembly_pose2 - assemble
		camera1 - camera
		box1 box2 package1 - container
		base1 cap1 - graspable
		stand1 stand2 - stand)
  (:init
		(arm_at arm1 camera1)
		(arm_at arm2 stand2)
		(arm_canreach arm1 assembly_pose1)
		(arm_canreach arm1 box1)
		(arm_canreach arm1 box2)
		(arm_canreach arm1 camera1)
		(arm_canreach arm1 package1)
		(arm_canreach arm1 stand1)
		(arm_canreach arm2 assembly_pose2)
		(arm_canreach arm2 box1)
		(arm_canreach arm2 box2)
		(arm_canreach arm2 camera1)
		(arm_canreach arm2 stand2)
		(arm_gripped arm2 base1)
		(arm_vacuumed arm1 cap1)
		(free assembly_pose1)
		(free assembly_pose2)
		(free box1)
		(free box2)
		(free package1)
		(free stand1)
		(upward cap1))
  (:goal (and
		(packed cap1 base1 package1))))

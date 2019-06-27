# pyppddl-planner -- a Probabilistic Planner by Compilation into Classical Planners

A probabilistic planner to solve PPDDL problems by compilation into classical planning (in Python3). 
The planner can employ any off-the-shelf classical planner for problem solving, 
however, it requires to implement a small code to parse and refine the resulting 
plan of the classical planners.
Currently, the classical planners [FF], [OPTIC], and [MADAGASCAR] have been integrated.

[FF]: https://fai.cs.uni-saarland.de/hoffmann/ff.html
[OPTIC]: https://nms.kcl.ac.uk/planning/software/optic.html
[MADAGASCAR]: https://users.aalto.fi/~rintanj1/jussi/satplan.html


## Requirement

Make sure you have the `ply` library installed on your system. 
To install it, run the following command line into the terminal:

```
$ pip3 install ply
```


## Usage

```
$ python3 main.py <DOMAIN> <PROBLEM> [<PLANNER>] [-v | --verbose]
```

for example following command runs the planner using the `FF` to solve a `pickit` problem:

```
$ python3 main.py domains/pickit_seq/pickit.pddl domains/pickit_seq/prob0.pddl planners/ff
```

or using `OPTIC` planner:

```
$ python3 main.py domains/pickit_seq/pickit.pddl domains/pickit_seq/prob0.pddl planners/optic-clp
```

or using `MADAGASCAR` planner:

```
$ python3 main.py domains/pickit_seq/pickit.pddl domains/pickit_seq/prob0.pddl planners/M
```


## Output plan

The output plan is a sequence of steps (i.e., each step may contain more than one action).
The numbers represent the order of the execution of the steps.
Steps in each line is followed by some conditions under which the next step is chosen.
Empty conditions are true conditions and usually appear for deterministic actions.
Some steps (i.e., steps containing probabilistic actions) have more than one conditions.
Conditions are, in fact, the different possible effects of the probabilistic actions.
The number after each condition represents the next step for the execution.


```
$ python3 main.py domains/pickit_seq/pickit.pddl domains/pickit_seq/prob0.pddl planners/ff

@ plan
 0 : (move_to_grasp arm1 box1 cap1 box1) -- () 1
 1 : (move_to_grasp arm2 box2 base1 box2) -- () 2
 2 : (vacuum_object arm2 base1 box2) -- () 3
 3 : (carry_to_camera arm2 base1 box2 camera1) -- () 4
 4 : (check_bottom_up arm2 base1 camera1) -- ((bottom_up base1) (camera_checked base1)) 5 -- ((top_up base1) (camera_checked base1)) 6
 5 : (carry_to_peg arm2 base1 camera1 peg1) -- () 7
 6 : (rotate_object arm2 base1) -- () 5
 7 : (put_in_peg arm2 base1 peg1) -- () 8
 8 : (move_to_grasp arm2 peg1 base1 peg1) -- () 9
 9 : (grip_object arm2 base1 peg1) -- () 10
10 : (carry_to_assemble arm2 base1 peg1 assembly_pose2) -- () 11
11 : (vacuum_object arm1 cap1 box1) -- () 12
12 : (carry_to_camera arm1 cap1 box1 camera1) -- () 13
13 : (check_bottom_up arm1 cap1 camera1) -- ((bottom_up cap1) (camera_checked cap1)) 14 -- ((top_up cap1) (camera_checked cap1)) 15
14 : (carry_to_hole arm1 cap1 camera1 hole1) -- () 16
15 : (rotate_object arm1 cap1) -- () 14
16 : (put_in_hole arm1 cap1 hole1) -- () 17
17 : (move_to_grasp arm1 hole1 cap1 hole1) -- () 18
18 : (grip_object arm1 cap1 hole1) -- () 19
19 : (carry_to_assemble arm1 cap1 hole1 assembly_pose1) -- () 20
20 : (assemble arm1 arm2 cap1 base1 assembly_pose1 assembly_pose2) -- () 21
21 : (ungrip_object arm2 cap1 base1) -- () 22
22 : (carry_to_pack arm1 cap1 base1 assembly_pose1 package1) -- () 23
23 : (put_in_pack arm1 cap1 base1 package1) -- () 24
24 : Goal achieved!
```

## Use the planner as a library

In `main.py` the function `parse_plan()` is a sample code to parse and output the resulting plan.


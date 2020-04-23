# Safe-Planner -- a Non-Deterministic Planner by Compilation into Classical Problems

Safe-Planner (SP) is an off-line non-deterministic planning algorithm based on replanning which compiles a Fully Observable Non-Deterministic (FOND) planning problem into a set of classical planning problems which can be solved using a classical problem solver. SP then merges the obtained classical solutions and forms a non-deterministic solution policy to the original non-deterministic problem. SP avoids dead-end states by simulating the execution during the policy generation and therefore it generates safe policies. The execution of a safe policy is guaranteed to terminate in a goal state for all potential outcomes of the actions in the non-deterministic environment (if any exists).

SP can employ any off-the-shelf classical planner for problem solving. Currently, the classical planners [FF], [OPTIC], [MADAGASCAR], [VHPOP], and [LPG-TD] have been integrated.

[FF]: https://fai.cs.uni-saarland.de/hoffmann/ff.html
[OPTIC]: https://nms.kcl.ac.uk/planning/software/optic.html
[MADAGASCAR]: https://users.aalto.fi/~rintanj1/jussi/satplan.html
[VHPOP]: http://www.tempastic.org/vhpop/
[LPG-TD]: https://lpg.unibs.it/lpg/


## Requirement

SP has been implemented in `Python` and the following packages are required to install: 

In Python2:
```
$ sudo apt install python-pip
$ pip install ply graphviz
```

In Python3
```
$ sudo apt install python3-pip
$ pip3 install ply graphviz
```

Also install the following `Lua` libraries:
```
$ sudo apt install -y lua-penlight lua-json luarocks lua-ansicolors libgv-lua
$ sudo luarocks install ansicolors graphviz
```

## Usage

```
$ python3 main.py <DOMAIN> <PROBLEM> [-c <PLANNER>] [-p] [-d] [-j] [-s] [-v N] [-h]
```

for example following command runs the planner using the `FF` to solve a `pickit` problem:

```
$ python3 main.py domains/pickit/domain.pddl domains/pickit/prob0.pddl -c planners/ff
```

or using `OPTIC` planner:

```
$ python3 main.py domains/pickit/domain.pddl domains/pickit/prob0.pddl -c planners/optic-clp
```

or using `MADAGASCAR` planner:

```
$ python3 main.py domains/pickit/domain.pddl domains/pickit/prob0.pddl -c planners/M
```


## The planner's output

The output plan is a sequence of steps (i.e., each step may contain more than one action). The numbers represent the order of the execution of the steps. Steps in each line is followed by some conditions under which the next step is chosen. Empty conditions are true conditions and usually appear for deterministic actions. Some steps (i.e., steps containing nondeterministic actions) have more than one conditions. Conditions are, in fact, the different possible effects of the nondeterministic actions. The number after each condition represents the next step for the execution.


```
$ python3 main.py domains/pickit/domain.pddl domains/pickit/prob0.pddl -c ff

@ PLAN
 0 : (move_to_grasp arm2 stand2 box2 base1) -- () 1
 1 : (move_to_grasp arm1 stand1 box1 cap1) -- () 2
 2 : (vacuum_object arm2 base1 box2) -- () 3
 3 : (vacuum_object arm1 cap1 box1) -- () 4
 4 : (carry_to_camera arm2 box2 camera1 base1) -- () 5
 5 : (check_orientation arm2 base1 camera1) -- ((downward base1))((unknown_orientation base1)) 6 -- ((upward base1))((unknown_orientation base1)) 7
 6 : (carry_to_stand arm2 camera1 stand2 base1) -- () 8
 7 : (rotate arm2 base1) -- () 6
 8 : (carry_to_camera arm1 box1 camera1 cap1) -- () 9
 9 : (check_orientation arm1 cap1 camera1) -- ((downward cap1))((unknown_orientation cap1)) 10 -- ((upward cap1))((unknown_orientation cap1)) 11
10 : (put_object arm2 base1 stand2) -- () 12
11 : (rotate arm1 cap1) -- () 10
12 : (carry_to_stand arm1 camera1 stand1 cap1) -- () 13
13 : (put_object arm1 cap1 stand1) -- () 14
14 : (grip_object arm2 base1 stand2) -- () 15
15 : (carry_to_assemble arm2 stand2 assembly_pose2 base1) -- () 16
16 : (grip_object arm1 cap1 stand1) -- () 17
17 : (carry_to_assemble arm1 stand1 assembly_pose1 cap1) -- () 18
18 : (assemble arm1 arm2 cap1 base1 assembly_pose1 assembly_pose2) -- () 19
19 : (ungrip_object arm2 base1) -- () 20
20 : (carry_to_pack arm1 assembly_pose1 package1 cap1) -- () 21
21 : (pack_object arm1 cap1 base1 package1) -- () GOAL
```




```
$ python3 main.py domains/pickit/domain.pddl domains/pickit/prob0.pddl -c lpg-td

@ plan
 0 : (move_to_grasp arm1 stand1 box1 cap1) (move_to_grasp arm2 stand2 box2 base1) -- () 1
 1 : (vacuum_object arm1 cap1 box1) (vacuum_object arm2 base1 box2) -- () 2
 2 : (carry_to_camera arm1 box1 camera1 cap1) -- () 3
 3 : (check_orientation arm1 cap1 camera1) -- ((upward cap1))((unknown_orientation cap1)) 4 -- ((downward cap1))((unknown_orientation cap1)) 5
 4 : (rotate arm1 cap1) (carry_to_stand arm1 camera1 stand1 cap1) -- () 6
 5 : (carry_to_stand arm1 camera1 stand1 cap1) -- () 6
 6 : (put_object arm1 cap1 stand1) (carry_to_camera arm2 box2 camera1 base1) -- () 7
 7 : (grip_object arm1 cap1 stand1) (check_orientation arm2 base1 camera1) -- ((arm_gripped arm1 cap1) (upward base1))((object_at cap1 stand1) (arm_free arm1) (unknown_orientation base1)) 8 -- ((arm_gripped arm1 cap1) (downward base1))((object_at cap1 stand1) (arm_free arm1) (unknown_orientation base1)) 9
 8 : (rotate arm2 base1) (carry_to_stand arm2 camera1 stand2 base1) (carry_to_assemble arm1 stand1 assembly_pose1 cap1) -- () 10
 9 : (carry_to_stand arm2 camera1 stand2 base1) (carry_to_assemble arm1 stand1 assembly_pose1 cap1) -- () 10
10 : (put_object arm2 base1 stand2) -- () 11
11 : (grip_object arm2 base1 stand2) -- () 12
12 : (carry_to_assemble arm2 stand2 assembly_pose2 base1) -- () 13
13 : (assemble arm1 arm2 cap1 base1 assembly_pose1 assembly_pose2) -- () 14
14 : (ungrip_object arm2 base1) (carry_to_pack arm1 assembly_pose1 package1 cap1) -- () 15
15 : (pack_object arm1 cap1 base1 package1) -- () GOAL
```

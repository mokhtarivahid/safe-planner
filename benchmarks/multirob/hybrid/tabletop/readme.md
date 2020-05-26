## Tabletop Object Manipulation Domain

In order to demonstrate and validate the practical utility 
of our work, we develop a FOND tabletop object manipulation
domain including an automated workspace with a dual-arm 
manipulator and a set of small and large objects on a table. 
The task is to pick up a target large object. 
Objects can be grasped at left, right and top grasp poses.
The constraints are that some object might obstruct the 
(left/right) grasp pose of other objects and some objects 
might be reachable by only one arm.
We implement a non-deterministic action single-arm-pickup
with three stochastic outcomes: (i) an object might be 
picked up successfully (intended effect); (ii) an object 
might fall down on the table (unintended effect); and (iii) 
a large object might fall down and slips from the table 
(unintended effect). 
We alternatively implement a deterministic action 
dual-arm-pickup to pick up any type of objects 
successfully.
The domain allows for picking up a large object with both 
single and dual-arm actions, however, SP never picks up 
a large object by a single arm since it might result in a 
dead end state (the latter outcome).
For the purpose of the domain modeling language, we use the 
Probabilistic Planning Domain Description Language (PPDDL) 
by an extension for FOND planning domains with oneof clauses 
in the action effects. Other deterministic actions in this domain 
include grasp, ungrasp, single-arm-putdown and dual-arm-putdown.
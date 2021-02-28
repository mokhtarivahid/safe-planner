# Safe-Planner - A Single-Outcome Replanner for Computing Strong Cyclic Solutions in Fully Observable Non-Deterministic Domains

**Safe-Planner (SP)** is an off-line non-deterministic planning algorithm based on replanning that compiles a **Fully Observable Non-Deterministic (FOND)** planning problem into a set of classical planning problems which can be solved using a classical problem solver. SP then merges the obtained classical solutions and forms a non-deterministic solution policy to the original non-deterministic problem. SP avoids dead-end states by 
modifying a planning problem such that it prevents a classical planner to generate weak plans involving actions leading to dead-ends and therefore it generates safe policies. The execution of a safe policy is guaranteed to terminate in a goal state for all potential outcomes of the actions in the non-deterministic environment (if any exists).

SP can employ any off-the-shelf classical planner for problem solving. Currently, the classical planners [FF], [OPTIC], [MADAGASCAR], [PROBE], [VHPOP], [LPG-TD], [LPG], and [FAST-DOWNWARD] have been integrated. 

**Note:** OPTIC, MADAGASCAR, VHPOP, and LPG-TD are temporal/partial-order planners and therefore the produced policies are also partial-order.

[FF]: https://fai.cs.uni-saarland.de/hoffmann/ff.html
[OPTIC]: https://nms.kcl.ac.uk/planning/software/optic.html
[MADAGASCAR]: https://users.aalto.fi/~rintanj1/jussi/satplan.html
[VHPOP]: http://www.tempastic.org/vhpop/
[LPG-TD]: https://lpg.unibs.it/lpg/
[LPG]: https://lpg.unibs.it/lpg/
[FAST-DOWNWARD]: http://www.fast-downward.org/
[PROBE]: https://github.com/aig-upf/probe



## Contents
1. [Requirement](#requirement)
2. [PPDDL](#ppddl)
3. [Usage](#usage)
4. [The planner output](#the-planner-output)



## Requirement

SP has been implemented in `Python3` and the following packages are required to install: 

```bash
sudo apt install python3-pip
pip3 install ply
```

### optional

For running with `-j` parameter and translating plans into json, also install:

```bash
sudo apt install -y graphviz-dev
pip3 install graphviz pygraphviz
```

and the following `Lua` libraries (optional: only for parsing json files):

```bash
sudo apt install -y lua-penlight lua-json lua-ansicolors luarocks
sudo luarocks install graphviz
```



## PPDDL

Safe-Planner uses the **Probabilistic Planning Domain Definition Language (PPDDL)** as the domain modeling language with ``oneof`` clauses in actions' effects. PPDDL is an extension of the standard PDDL to support probabilistic or non-deterministic outcomes in the actions' descriptions. A description of PPDDL is available at http://reports-archive.adm.cs.cmu.edu/anon/2004/CMU-CS-04-167.pdf. 

A helpful collection of materials for AI Planning and PDDL are also provided at https://planning.wiki.

A useful introduction to learning PDDL is also available at https://fareskalaboud.github.io/LearnPDDL.

#### PDDL supported

Safe-Planner is strongly dependent on the employed external classical planners, so the given planning domains and problems are firstly required to be supported by the external classical planners.

Apart from the PDDL support of the external planners, Safe-Planner also supports limited but most useful features of the PDDL. Particularly, Safe-Planner supports the following PDDL requirements: `:strips`, `:typing`, `:equality`, `:negative-preconditions`, `:existential-preconditions`, `:universal-preconditions`, `:conditional-effects`, `:probabilistic-effects`.

More precisely, the following combinations are supported by Safe-Planner for modeling action effects:

##### conditional effects

```
(when (conditions) (effects))
```

```
(forall (variables list) (effects))
```

```
(forall (variables list) (when (conditions) (effects)))
```

##### non-deterministic effects

```
(oneof (effects)
       (when (conditions) (effects))
       (forall (variables list) (effects))
       (forall (variables list) (when (conditions) (effects)))
       ...)
```

```
(probabilistic P (effects)
               P (when (conditions) (effects))
               P (forall (variables list) (effects))
               P (forall (variables list) (when (conditions) (effects)))
               ...)
```



**Note:** currently, Safe-Planner does not support **untyped** objects, so when modeling a planning domain always use a type for objects.



## Usage


```bash
# using the 'sp' script
./sp <DOMAIN> <PROBLEM> [-c <PLANNERS_LIST>] [-r] [-a] [-d] [-j] [-s] [-v 1|2]
```

```bash
# for ease of use, one can only pass a problem file, however 'domain.pddl' must be in the same directory
./sp <PROBLEM> [-c <PLANNERS_LIST>] [-r] [-a] [-d] [-j] [-s] [-v 1|2]
```
```bash
# in case of both domain and problem in one file
./sp <FILE> [-c <PLANNERS_LIST>] [-r] [-a] [-d] [-j] [-s] [-v 1|2]
```

```bash
# using python3 command in the directory 'src/' (cd src/)
python3 main.py <DOMAIN> <PROBLEM> [-c <PLANNERS_LIST>] [-r] [-a] [-d] [-j] [-s] [-v 1|2]
```



### optional parameters

`-c <PLANNERS_LIST>`: a list of planners for dual planning mode, e.g., `-c ff` or `-c ff m` or `-c ff m fd`, ...

`-r`: reverse the ranking of the classical domains when compiling from non-deterministic to deterministic. The default ranking is Descending according to the length of actions' effects (note that it does not guarantee always to improve the performance, however, in some domains it dramatically improves the performance by avoiding producing misleading plans).

`-a`: compile the non-deterministic domain into one classical domain using the all-outcome compilation strategy (the default compilation strategy is the single-outcome which translates into a set of ordered classical domains).

`-d`: draw graphically the plan in the dot format.

`-j`: translate the produced plan into a json file [experimental].

`-s`: record the planner's performance in `.stat` file.

`-v 1|2`: increase verbosity.



##### The following commands show some examples on how to run Safe-Planner on individual problems:

```bash
# run Safe-Planner using external planner FF (the default planner)
./sp benchmarks/fond-domains/elevators/domain.pddl benchmarks/fond-domains/elevators/p01.pddl 

# run Safe-Planner using external planners FF and Madagascar (dual replanning) with default ranking (Descending)
./sp benchmarks/fond-domains/elevators/domain.pddl benchmarks/fond-domains/elevators/p01.pddl -c ff m

# run Safe-Planner using external planners FF and Madagascar with reverse ranking (Ascending)
./sp benchmarks/fond-domains/elevators/domain.pddl benchmarks/fond-domains/elevators/p01.pddl -c ff m -r
```

##### or in batch:

```bash
# cd src/
# run Safe-Planner in batch for each used FOND domain within 30m for each problem
./batch-run.sh ../benchmarks/fond-domains/acrobatics -r -c ff m
./batch-run.sh ../benchmarks/fond-domains/beam-walk -c ff m
./batch-run.sh ../benchmarks/fond-domains/blocksworld -c ff m
./batch-run.sh ../benchmarks/fond-domains/elevators -c ff m
./batch-run.sh ../benchmarks/fond-domains/ex-blocksworld -c ff m
./batch-run.sh ../benchmarks/fond-domains/first-responders -c ff m
./batch-run.sh ../benchmarks/fond-domains/forest -c ff m
./batch-run.sh ../benchmarks/fond-domains/tireworld -c ff m
./batch-run.sh ../benchmarks/fond-domains/triangle-tireworld -c ff m
./batch-run.sh ../benchmarks/fond-domains/zenotravel -c ff m
./batch-run.sh ../benchmarks/fond-domains/doors -r -c ff m
./batch-run.sh ../benchmarks/fond-domains/islands -r -c ff m
./batch-run.sh ../benchmarks/fond-domains/miner -r -c ff m
./batch-run.sh ../benchmarks/fond-domains/tireworld-spiky -r -c ff m
./batch-run.sh ../benchmarks/fond-domains/tireworld-truck -r -c ff m
```


```bash
# run Safe-Planner in batch for all FOND domains in dual replanning mode 
# using ff and m planners in both single-outcome (safe-planner algorithm) 
# and all-outcome (ndp2 algorithm)
./batch-run-fond.sh 
```



## The planner output

SP represent a policy as a sequence of numbered steps such that:

- Each step contains either a set of actions in one of the following formats:

    ```number : {actions} -- {} number/GOAL```

    ```number : {actions} -- {add_list} number/GOAL ...```

    ```number : {actions} -- {add_list} \ {del_list} number/GOAL ...```

- Each `number` represents the order/level of the execution of each step; 

- The set of actions `{actions}` at each step are followed by sets of conditions under which next steps are chosen (sets of conditions comes after one `--` for each outcome)  ; 

- Conditions are the different possible outcomes of actions in a step; 

- Empty conditions `{}` are true conditions and only appear for deterministic actions in a step; 

- Steps containing nondeterministic actions have more than one conditions and outcomes;

- Conditions include a set of `{add_list}` and a set of `{del_list}` (if any) of a nondeterministic step, that is, the effects added to a new state and the effects removed from the old state after the step is applied;

- The `number` after each condition represents the next step for the execution;

- The keyword `GOAL`  after a condition means the goal is achieved by that step.



##### Example 1: [`bus-fare`](benchmarks/prob_interesting/bus-fare.pddl) domain


```bash
./sp benchmarks/prob_interesting/bus-fare.pddl -j -d

@ PLAN
 0 : {(wash-car-1)} -- {(have-2-coin)} \ {(have-1-coin)} 1 -- {(have-1-coin)} 0
 1 : {(bet-coin-2)} -- {(have-1-coin)} \ {(have-2-coin)} 0 -- {(have-3-coin)} \ {(have-2-coin)} 2
 2 : {(buy-fare)} -- {} GOAL
```

the optional parameter `-d` translates the produced plan into a dot file in the same path:

![bus-fare](resources/bus-fare.png)

[**EXPERIMENTAL!**] the optional parameter `-j` translates the produced plan into a json file in the same path:

```json
{
    "plan": [
        "step_0", 
        "step_1", 
        "step_2"
    ],
    "step_0": {
        "actions": [
            {"name": "wash-car-1", "arguments": []}
        ],
        "outcomes": [
            {"next": "step_1", "condition": ["(have-2-coin)"]}, 
            {"next": "step_0", "condition": ["(have-1-coin)"]}
        ]
    },
    "step_1": {
        "actions": [{"name": "bet-coin-2", "arguments": []}
        ],
        "outcomes": [
            {"next": "step_0", "condition": ["(have-1-coin)"]},
            {"next": "step_2", "condition": ["(have-3-coin)"]}
        ]
    },
    "step_2": {
        "actions": [
            {"name": "buy-fare", "arguments": []}
        ],
        "outcomes": [
            {"next": "GOAL", "condition": ["(have-fare)"]}
        ]
    }
}
```


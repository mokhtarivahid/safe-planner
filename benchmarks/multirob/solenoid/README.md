## The PDDL domain for IROS 2021 paper on composable skills. 

Please note that currently `Safe-Planner` does not support the temporal encoding in PDDL2.1, so the `solenoid` domain encoding was adapted to PDDL1.0.

### Running

In this version, we have to introduce the used **agents** and the **temporal actions** as follows:

##### using optic-clp planner

run the command below in the main directory of safe-planner:

```bash
python3 json_ma_plan_iros21.py benchmarks/multirob/solenoid/domain.pddl benchmarks/multirob/solenoid/prob1_1.pddl -c optic-clp -a left_arm right_arm -t avoid_collision admittance_control -d
```

this will generate the following files:

```bash
# the output plan in json
-- plan_json_file:benchmarks/multirob/solenoid/prob1_1.plan.json

# the output actions in json
-- actions_json_file:benchmarks/multirob/solenoid/prob1_1.actions.json

# the graphical representation of the output plan in dot
-- graphical plan_json_file:benchmarks/multirob/solenoid/prob1_1.plan.json.dot
```

when the optional parameter `-d` is used:

```bash
# the original output plan in dot
-- plan in dot file: benchmarks/multirob/solenoid/prob1_1.dot

# the output plan in a precedence graph
-- precedence graph: benchmarks/multirob/solenoid/prob1_1.gv

# the transitive reduction of the precedence graph
-- transitive reduction: benchmarks/multirob/solenoid/prob1_1.tred.gv
```
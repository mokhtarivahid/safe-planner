
echo "file,problem,planning_time,singlesoutcome_planning_call,alloutcome_planning_call,unsolvable_states,solvable,policy_length,plan_length" > benchmarks/ipc2008/faults/results.csv

echo "benchmarks/ipc2008/faults/p_1_1.pddl"
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_1_1.pddl benchmarks/ipc2008/faults/p_1_1.pddl -d -s`
echo "benchmarks/ipc2008/faults/p_2_1.pddl"
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_2_1.pddl benchmarks/ipc2008/faults/p_2_1.pddl -d -s`
echo "benchmarks/ipc2008/faults/p_2_2.pddl"
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_2_2.pddl benchmarks/ipc2008/faults/p_2_2.pddl -d -s`
echo "benchmarks/ipc2008/faults/p_3_1.pddl"
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_3_1.pddl benchmarks/ipc2008/faults/p_3_1.pddl -d -s`
echo "benchmarks/ipc2008/faults/p_3_2.pddl"
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_3_2.pddl benchmarks/ipc2008/faults/p_3_2.pddl -d -s`
echo "benchmarks/ipc2008/faults/p_3_3.pddl"
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_3_3.pddl benchmarks/ipc2008/faults/p_3_3.pddl -d -s`
echo "benchmarks/ipc2008/faults/p_4_1.pddl"
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_4_1.pddl benchmarks/ipc2008/faults/p_4_1.pddl -d -s`
echo "benchmarks/ipc2008/faults/p_4_2.pddl"
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_4_2.pddl benchmarks/ipc2008/faults/p_4_2.pddl -d -s`
echo "benchmarks/ipc2008/faults/p_4_3.pddl"
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_4_3.pddl benchmarks/ipc2008/faults/p_4_3.pddl -d -s`
echo "benchmarks/ipc2008/faults/p_4_4.pddl"
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_4_4.pddl benchmarks/ipc2008/faults/p_4_4.pddl -d -s`
echo "benchmarks/ipc2008/faults/p_5_1.pddl"
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_5_1.pddl benchmarks/ipc2008/faults/p_5_1.pddl -d -s`
echo "benchmarks/ipc2008/faults/p_5_2.pddl"
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_5_2.pddl benchmarks/ipc2008/faults/p_5_2.pddl -d -s`
echo "benchmarks/ipc2008/faults/p_5_3.pddl"
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_5_3.pddl benchmarks/ipc2008/faults/p_5_3.pddl -d -s`
echo "benchmarks/ipc2008/faults/p_5_4.pddl"
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_5_4.pddl benchmarks/ipc2008/faults/p_5_4.pddl -d -s`
echo "benchmarks/ipc2008/faults/p_5_5.pddl"
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_5_5.pddl benchmarks/ipc2008/faults/p_5_5.pddl -d -s`
echo "benchmarks/ipc2008/faults/p_6_1.pddl"
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_6_1.pddl benchmarks/ipc2008/faults/p_6_1.pddl -d -s`
echo "benchmarks/ipc2008/faults/p_6_2.pddl"
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_6_2.pddl benchmarks/ipc2008/faults/p_6_2.pddl -d -s`
echo "benchmarks/ipc2008/faults/p_6_3.pddl"
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_6_3.pddl benchmarks/ipc2008/faults/p_6_3.pddl -d -s`
echo "benchmarks/ipc2008/faults/p_6_4.pddl"
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_6_4.pddl benchmarks/ipc2008/faults/p_6_4.pddl -d -s`
echo "benchmarks/ipc2008/faults/p_6_5.pddl"
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_6_5.pddl benchmarks/ipc2008/faults/p_6_5.pddl -d -s`
echo "benchmarks/ipc2008/faults/p_6_6.pddl"
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_6_6.pddl benchmarks/ipc2008/faults/p_6_6.pddl -d -s`
echo "benchmarks/ipc2008/faults/p_7_1.pddl"
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_7_1.pddl benchmarks/ipc2008/faults/p_7_1.pddl -d -s`
echo "benchmarks/ipc2008/faults/p_7_2.pddl"
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_7_2.pddl benchmarks/ipc2008/faults/p_7_2.pddl -d -s`
echo "benchmarks/ipc2008/faults/p_7_3.pddl"
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_7_3.pddl benchmarks/ipc2008/faults/p_7_3.pddl -d -s`
echo "benchmarks/ipc2008/faults/p_7_4.pddl"
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_7_4.pddl benchmarks/ipc2008/faults/p_7_4.pddl -d -s`
echo "benchmarks/ipc2008/faults/p_7_5.pddl"
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_7_5.pddl benchmarks/ipc2008/faults/p_7_5.pddl -d -s`
echo "benchmarks/ipc2008/faults/p_7_6.pddl"
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_7_6.pddl benchmarks/ipc2008/faults/p_7_6.pddl -d -s`
echo "benchmarks/ipc2008/faults/p_7_7.pddl"
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_7_7.pddl benchmarks/ipc2008/faults/p_7_7.pddl -d -s`
echo "benchmarks/ipc2008/faults/p_8_1.pddl"
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_8_1.pddl benchmarks/ipc2008/faults/p_8_1.pddl -d -s`
echo "benchmarks/ipc2008/faults/p_8_2.pddl"
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_8_2.pddl benchmarks/ipc2008/faults/p_8_2.pddl -d -s`

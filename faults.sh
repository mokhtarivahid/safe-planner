planners=$1
planners_dir=$1

if [ "$2" != "" ]; then planners+=" $2"; planners_dir+="_$2"; fi
if [ "$3" != "" ]; then planners+=" $3"; planners_dir+="_$3"; fi
if [ "$4" != "" ]; then planners+=" $4"; planners_dir+="_$4"; fi
if [ "$5" != "" ]; then planners+=" $5"; planners_dir+="_$5"; fi
if [ "$6" != "" ]; then planners+=" $6"; planners_dir+="_$6"; fi
if [ "$7" != "" ]; then planners+=" $7"; planners_dir+="_$7"; fi
if [ "$8" != "" ]; then planners+=" $8"; planners_dir+="_$8"; fi
if [ "$9" != "" ]; then planners+=" $9"; planners_dir+="_$9"; fi

if [ "$planners" == "" ]; then planners="ff"; planners_dir="ff"; fi

echo $planners
faults="benchmarks/ipc2008/faults"
rm -f $faults/*dot 
rm -f $faults/*stat
echo "file,problem,planning_time,singlesoutcome_planning_call,alloutcome_planning_call,unsolvable_states,solvable,policy_length,plan_length" > $faults/results.csv

echo "benchmarks/ipc2008/faults/p_1_1.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_1_1.pddl benchmarks/ipc2008/faults/p_1_1.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_2_1.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_2_1.pddl benchmarks/ipc2008/faults/p_2_1.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_2_2.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_2_2.pddl benchmarks/ipc2008/faults/p_2_2.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_3_1.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_3_1.pddl benchmarks/ipc2008/faults/p_3_1.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_3_2.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_3_2.pddl benchmarks/ipc2008/faults/p_3_2.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_3_3.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_3_3.pddl benchmarks/ipc2008/faults/p_3_3.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_4_1.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_4_1.pddl benchmarks/ipc2008/faults/p_4_1.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_4_2.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_4_2.pddl benchmarks/ipc2008/faults/p_4_2.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_4_3.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_4_3.pddl benchmarks/ipc2008/faults/p_4_3.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_4_4.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_4_4.pddl benchmarks/ipc2008/faults/p_4_4.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_5_1.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_5_1.pddl benchmarks/ipc2008/faults/p_5_1.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_5_2.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_5_2.pddl benchmarks/ipc2008/faults/p_5_2.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_5_3.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_5_3.pddl benchmarks/ipc2008/faults/p_5_3.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_5_4.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_5_4.pddl benchmarks/ipc2008/faults/p_5_4.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_5_5.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_5_5.pddl benchmarks/ipc2008/faults/p_5_5.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_6_1.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_6_1.pddl benchmarks/ipc2008/faults/p_6_1.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_6_2.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_6_2.pddl benchmarks/ipc2008/faults/p_6_2.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_6_3.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_6_3.pddl benchmarks/ipc2008/faults/p_6_3.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_6_4.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_6_4.pddl benchmarks/ipc2008/faults/p_6_4.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_6_5.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_6_5.pddl benchmarks/ipc2008/faults/p_6_5.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_6_6.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_6_6.pddl benchmarks/ipc2008/faults/p_6_6.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_7_1.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_7_1.pddl benchmarks/ipc2008/faults/p_7_1.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_7_2.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_7_2.pddl benchmarks/ipc2008/faults/p_7_2.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_7_3.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_7_3.pddl benchmarks/ipc2008/faults/p_7_3.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_7_4.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_7_4.pddl benchmarks/ipc2008/faults/p_7_4.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_7_5.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_7_5.pddl benchmarks/ipc2008/faults/p_7_5.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_7_6.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_7_6.pddl benchmarks/ipc2008/faults/p_7_6.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_7_7.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_7_7.pddl benchmarks/ipc2008/faults/p_7_7.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_8_1.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_8_1.pddl benchmarks/ipc2008/faults/p_8_1.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_8_2.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_8_2.pddl benchmarks/ipc2008/faults/p_8_2.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_8_3.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_8_3.pddl benchmarks/ipc2008/faults/p_8_3.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_8_4.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_8_4.pddl benchmarks/ipc2008/faults/p_8_4.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_8_5.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_8_5.pddl benchmarks/ipc2008/faults/p_8_5.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_8_6.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_8_6.pddl benchmarks/ipc2008/faults/p_8_6.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_8_7.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_8_7.pddl benchmarks/ipc2008/faults/p_8_7.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_8_8.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_8_8.pddl benchmarks/ipc2008/faults/p_8_8.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_9_1.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_9_1.pddl benchmarks/ipc2008/faults/p_9_1.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_9_2.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_9_2.pddl benchmarks/ipc2008/faults/p_9_2.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_9_3.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_9_3.pddl benchmarks/ipc2008/faults/p_9_3.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_9_4.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_9_4.pddl benchmarks/ipc2008/faults/p_9_4.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_9_5.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_9_5.pddl benchmarks/ipc2008/faults/p_9_5.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_9_6.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_9_6.pddl benchmarks/ipc2008/faults/p_9_6.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_9_7.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_9_7.pddl benchmarks/ipc2008/faults/p_9_7.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_9_8.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_9_8.pddl benchmarks/ipc2008/faults/p_9_8.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_9_9.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_9_9.pddl benchmarks/ipc2008/faults/p_9_9.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_10_1.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_10_1.pddl benchmarks/ipc2008/faults/p_10_1.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_10_2.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_10_2.pddl benchmarks/ipc2008/faults/p_10_2.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_10_3.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_10_3.pddl benchmarks/ipc2008/faults/p_10_3.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_10_4.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_10_4.pddl benchmarks/ipc2008/faults/p_10_4.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_10_5.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_10_5.pddl benchmarks/ipc2008/faults/p_10_5.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_10_6.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_10_6.pddl benchmarks/ipc2008/faults/p_10_6.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_10_7.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_10_7.pddl benchmarks/ipc2008/faults/p_10_7.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_10_8.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_10_8.pddl benchmarks/ipc2008/faults/p_10_8.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_10_9.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_10_9.pddl benchmarks/ipc2008/faults/p_10_9.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

echo "benchmarks/ipc2008/faults/p_10_10.pddl"
start_time=`date +%s%N`
output=`timeout 1800 nice -n 0 python3 main.py benchmarks/ipc2008/faults/d_10_10.pddl benchmarks/ipc2008/faults/p_10_10.pddl -d -s -c $planners`
end_time=`date +%s%N`
runingtime=$(((end_time-start_time)/1000000))
echo ' ['$((runingtime/1000)).$((runingtime%1000))']'

rm -fr $faults/$planners_dir
mkdir -p $faults/$planners_dir
mv $faults/*dot $faults/$planners_dir 2>/dev/null
mv $faults/*stat $faults/$planners_dir 2>/dev/null
mv $faults/*csv $faults/$planners_dir/$planners_dir.csv 2>/dev/null

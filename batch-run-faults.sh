#!/bin/bash
##
# @Description: run the planner in batch of problems in a directory
##
declare -a arr=("benchmarks/fond-domains/faults/d_1_1.pddl benchmarks/fond-domains/faults/p_1_1.pddl"
                "benchmarks/fond-domains/faults/d_2_1.pddl benchmarks/fond-domains/faults/p_2_1.pddl"
                "benchmarks/fond-domains/faults/d_2_2.pddl benchmarks/fond-domains/faults/p_2_2.pddl"
                "benchmarks/fond-domains/faults/d_3_1.pddl benchmarks/fond-domains/faults/p_3_1.pddl"
                "benchmarks/fond-domains/faults/d_3_2.pddl benchmarks/fond-domains/faults/p_3_2.pddl"
                "benchmarks/fond-domains/faults/d_3_3.pddl benchmarks/fond-domains/faults/p_3_3.pddl"
                "benchmarks/fond-domains/faults/d_4_1.pddl benchmarks/fond-domains/faults/p_4_1.pddl"
                "benchmarks/fond-domains/faults/d_4_2.pddl benchmarks/fond-domains/faults/p_4_2.pddl"
                "benchmarks/fond-domains/faults/d_4_3.pddl benchmarks/fond-domains/faults/p_4_3.pddl"
                "benchmarks/fond-domains/faults/d_4_4.pddl benchmarks/fond-domains/faults/p_4_4.pddl"
                "benchmarks/fond-domains/faults/d_5_1.pddl benchmarks/fond-domains/faults/p_5_1.pddl"
                "benchmarks/fond-domains/faults/d_5_2.pddl benchmarks/fond-domains/faults/p_5_2.pddl"
                "benchmarks/fond-domains/faults/d_5_3.pddl benchmarks/fond-domains/faults/p_5_3.pddl"
                "benchmarks/fond-domains/faults/d_5_4.pddl benchmarks/fond-domains/faults/p_5_4.pddl"
                "benchmarks/fond-domains/faults/d_5_5.pddl benchmarks/fond-domains/faults/p_5_5.pddl"
                "benchmarks/fond-domains/faults/d_6_1.pddl benchmarks/fond-domains/faults/p_6_1.pddl"
                "benchmarks/fond-domains/faults/d_6_2.pddl benchmarks/fond-domains/faults/p_6_2.pddl"
                "benchmarks/fond-domains/faults/d_6_3.pddl benchmarks/fond-domains/faults/p_6_3.pddl"
                "benchmarks/fond-domains/faults/d_6_4.pddl benchmarks/fond-domains/faults/p_6_4.pddl"
                "benchmarks/fond-domains/faults/d_6_5.pddl benchmarks/fond-domains/faults/p_6_5.pddl"
                "benchmarks/fond-domains/faults/d_6_6.pddl benchmarks/fond-domains/faults/p_6_6.pddl"
                "benchmarks/fond-domains/faults/d_7_1.pddl benchmarks/fond-domains/faults/p_7_1.pddl"
                "benchmarks/fond-domains/faults/d_7_2.pddl benchmarks/fond-domains/faults/p_7_2.pddl"
                "benchmarks/fond-domains/faults/d_7_3.pddl benchmarks/fond-domains/faults/p_7_3.pddl"
                "benchmarks/fond-domains/faults/d_7_4.pddl benchmarks/fond-domains/faults/p_7_4.pddl"
                "benchmarks/fond-domains/faults/d_7_5.pddl benchmarks/fond-domains/faults/p_7_5.pddl"
                "benchmarks/fond-domains/faults/d_7_6.pddl benchmarks/fond-domains/faults/p_7_6.pddl"
                "benchmarks/fond-domains/faults/d_7_7.pddl benchmarks/fond-domains/faults/p_7_7.pddl"
                "benchmarks/fond-domains/faults/d_8_1.pddl benchmarks/fond-domains/faults/p_8_1.pddl"
                "benchmarks/fond-domains/faults/d_8_2.pddl benchmarks/fond-domains/faults/p_8_2.pddl"
                "benchmarks/fond-domains/faults/d_8_3.pddl benchmarks/fond-domains/faults/p_8_3.pddl"
                "benchmarks/fond-domains/faults/d_8_4.pddl benchmarks/fond-domains/faults/p_8_4.pddl"
                "benchmarks/fond-domains/faults/d_8_5.pddl benchmarks/fond-domains/faults/p_8_5.pddl"
                "benchmarks/fond-domains/faults/d_8_6.pddl benchmarks/fond-domains/faults/p_8_6.pddl"
                "benchmarks/fond-domains/faults/d_8_7.pddl benchmarks/fond-domains/faults/p_8_7.pddl"
                "benchmarks/fond-domains/faults/d_8_8.pddl benchmarks/fond-domains/faults/p_8_8.pddl"
                "benchmarks/fond-domains/faults/d_9_1.pddl benchmarks/fond-domains/faults/p_9_1.pddl"
                "benchmarks/fond-domains/faults/d_9_2.pddl benchmarks/fond-domains/faults/p_9_2.pddl"
                "benchmarks/fond-domains/faults/d_9_3.pddl benchmarks/fond-domains/faults/p_9_3.pddl"
                "benchmarks/fond-domains/faults/d_9_4.pddl benchmarks/fond-domains/faults/p_9_4.pddl"
                "benchmarks/fond-domains/faults/d_9_5.pddl benchmarks/fond-domains/faults/p_9_5.pddl"
                "benchmarks/fond-domains/faults/d_9_6.pddl benchmarks/fond-domains/faults/p_9_6.pddl"
                "benchmarks/fond-domains/faults/d_9_7.pddl benchmarks/fond-domains/faults/p_9_7.pddl"
                "benchmarks/fond-domains/faults/d_9_8.pddl benchmarks/fond-domains/faults/p_9_8.pddl"
                "benchmarks/fond-domains/faults/d_9_9.pddl benchmarks/fond-domains/faults/p_9_9.pddl"
                "benchmarks/fond-domains/faults/d_10_1.pddl benchmarks/fond-domains/faults/p_10_1.pddl"
                "benchmarks/fond-domains/faults/d_10_2.pddl benchmarks/fond-domains/faults/p_10_2.pddl"
                "benchmarks/fond-domains/faults/d_10_3.pddl benchmarks/fond-domains/faults/p_10_3.pddl"
                "benchmarks/fond-domains/faults/d_10_4.pddl benchmarks/fond-domains/faults/p_10_4.pddl"
                "benchmarks/fond-domains/faults/d_10_5.pddl benchmarks/fond-domains/faults/p_10_5.pddl"
                "benchmarks/fond-domains/faults/d_10_6.pddl benchmarks/fond-domains/faults/p_10_6.pddl"
                "benchmarks/fond-domains/faults/d_10_7.pddl benchmarks/fond-domains/faults/p_10_7.pddl"
                "benchmarks/fond-domains/faults/d_10_8.pddl benchmarks/fond-domains/faults/p_10_8.pddl"
                "benchmarks/fond-domains/faults/d_10_9.pddl benchmarks/fond-domains/faults/p_10_9.pddl"
                "benchmarks/fond-domains/faults/d_10_10.pddl benchmarks/fond-domains/faults/p_10_10.pddl")

time_out=1800  # timeout in s

function show_usage (){
    printf "Usage: $0 [-c <PLANNERS>] [-r] [-a] [-h] \n"
    printf "\n"
    printf "positional arguments:\n"
    printf " path\n"
    printf "      Path to the planning domain and problems\n"
    printf "\n"
    printf "optional arguments:\n"
    printf " -r|--rank\n"
    printf "      Rank the compiled domains in a descending order,\n"
    printf "      if not given, rank in an aescending order (default)\n"
    printf " -a|--all-outcome\n"
    printf "      Run the planner using only the all-outcome compilation\n"
#     printf " -d|--dot\n"
#     printf "      Draw a graph of the produced policy into a dot file\n"
#     printf " -s|--store\n"
#     printf "      Store the planner's performance in a '.stat' file\n"
    printf " -c|--planners\n"
    printf "      A list of planners: ff, fd, m, optic-clp, lpg-td, lpg, vhpop, ...\n"
    printf " -h|--help\n"
    printf "      Print help\n"
}

# [ "$#" -eq 0 ] && { show_usage; exit 1;}

args='-d -s'
planners=''
path='benchmarks/fond-domains/faults'

while [ ! -z "$1" ]; do
    case "$1" in
       --dot|-d)
           args+=" $1"
           ;;
       --store|-s)
           args+=" $1"
           ;;
       --all-outcome|-a)
           args+=" $1"
           ;;
       --rank|-r)
           args+=" $1"
           ;;
       --planners|-c)
           shift
           while [[ $1 != \-* && ! -z "$1" ]]; do
             planners+=" $1"
             shift
           done
           args+=" $1"
           ;;
       --help|-h)
          show_usage
          exit 1
          ;;
    esac
    shift  # Shift each argument out after processing them
done

if [ "$planners" == "" ]; then planners=" ff"; fi

# choose an output directory name
planners_dir="${planners// /_}(${args// /})"
planners_dir="${planners_dir:1}"
# planners_dir="${planners_dir:1}($(date '+%Y-%m-%d'))"

# choose a csv output file name
csv_file="${planners// /_}"
csv_file="${csv_file:1}".csv

echo $path
# echo "param:" $args
echo "planners:" $planners
echo "output:" $planners_dir/$csv_file

# remove the old files
rm -f $path/*dot 
rm -f $path/*stat

# create a temporary csv file for storing the results
echo $path/results.csv
echo "file,problem,planning_time,singlesoutcome_planning_call,alloutcome_planning_call,unsolvable_states,solvable,policy_length,plan_length" > $path/results.csv

## loop through the array
for i in "${arr[@]}"
do
  set -- $i
  domain=$1
  problem=$2

  printf $problem

  start_time=`date +%s%N`
  output=`timeout $time_out nice -n 0 python3 main.py $domain $problem $args -c $planners&`

  # check if timeout is over
  status=`echo $output | grep -c "@ PLAN"`
  if [[ $status -eq 0 ]]; then 
      echo ${problem##*/},0,0,0,0,0,0,0,0 >> $path/results.csv
  fi

  end_time=`date +%s%N`
  runingtime=$(((end_time-start_time)/1000000))
  echo ' ['$((runingtime/1000)).$((runingtime%1000))']'
  # rm -fr /tmp/safe-planner/*
done

# remove the old directory and make a new one
rm -fr $path/$planners_dir
mkdir -p $path/$planners_dir

# move the output files into the new directory
mv $path/*dot $path/$planners_dir 2>/dev/null
mv $path/*stat $path/$planners_dir 2>/dev/null
mv $path/*csv $path/$planners_dir/$csv_file 2>/dev/null

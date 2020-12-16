#!/bin/bash
##
# @Description: run the planner in batch of problems in a directory
##

time_out=1800  # timeout in s

function show_usage (){
    printf "Usage: $0 <PATH> [-c <PLANNERS>] [-r] [-a] [-h] \n"
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

[ "$#" -eq 0 ] && { show_usage; exit 1;}

args='-d -s'
planners=''
path=''
solver='SP'

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
           solver='NDP2'
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
       *)
          path=$1
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

# find the domain file
domain=$path/domain.pddl
echo $path
for problem in $path/*.pddl
do
  case $problem in
      *"domain.pddl"* ) continue;;
  esac

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

# copy also the output results in the 'results' directory
# choose an output solver name
solvers="${planners// /+}"
solvers="\$_{${solvers:1}}\$"

echo 'solvers:' "$solver${solvers^^}.csv"
echo "results/$(basename -- $path)"

# create a directory of the benchmark in the 'results' folder (if not any)
mkdir -p "results/$(basename -- $path)"
cp $path/$planners_dir/$csv_file "results/$(basename -- $path)/$solver${solvers^^}.csv" 2>/dev/null

echo

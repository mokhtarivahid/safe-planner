#!/bin/bash

time_out=1800  # timeout in s

run()
{
    path=$1 
    planners=$2
    planners_dir=$2

    if [ "$3" != "" ]; then planners+=" $3"; planners_dir+="_$3"; fi
    if [ "$4" != "" ]; then planners+=" $4"; planners_dir+="_$4"; fi
    if [ "$5" != "" ]; then planners+=" $5"; planners_dir+="_$5"; fi
    if [ "$6" != "" ]; then planners+=" $6"; planners_dir+="_$6"; fi
    if [ "$7" != "" ]; then planners+=" $7"; planners_dir+="_$7"; fi
    if [ "$8" != "" ]; then planners+=" $8"; planners_dir+="_$8"; fi
    if [ "$9" != "" ]; then planners+=" $9"; planners_dir+="_$9"; fi

    if [ "$planners" == "" ]; then planners="ff"; planners_dir="ff"; fi

    echo $path
    echo $planners
    echo $planners_dir

    rm -f $path/*dot 
    rm -f $path/*stat
    echo $path/results.csv
    echo "file,problem,planning_time,singlesoutcome_planning_call,alloutcome_planning_call,unsolvable_states,solvable,policy_length,plan_length" > $path/results.csv
    domain=$path/domain.pddl
    for problem in $path/*.pddl
    do
      case $problem in
          *"domain.pddl"* ) continue;;
      esac

      printf $problem

      start_time=`date +%s%N`
      output=`timeout $time_out nice -n 0 python3 main.py $domain $problem -d -s -r -c $planners&`

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
    rm -fr $path/$planners_dir
    mkdir -p $path/$planners_dir
    mv $path/*dot $path/$planners_dir 2>/dev/null
    mv $path/*stat $path/$planners_dir 2>/dev/null
    mv $path/*csv $path/$planners_dir/$planners_dir.csv 2>/dev/null
}

print_help()
{
        echo "Following options are allowed:"
        echo "./planner.sh <PATH> [<PLANNER>]       Solves problems in <PATH> using <PLANNER> (default <PLANNER>=ff)."
        echo "./planner.sh a <PATH> [<PLANNER>]   Solves all domains in <PATH> using <PLANNER> (default <PLANNER>=ff)."
}

if [ $# -eq 0 ]; then
    print_help
    exit 1
fi

case $1 in
   "h" | "")
        print_help
    ;;
   "a")
        domains=($2/*)
        for entry in ${domains[*]}; do
            run $entry $3 $4 $5 $6 $7 $8 $9
        done
    ;;
    *)
        # if [ ! -f "planners/$planner" ]
        # then
        #   echo "The planner '$planner' not found."
        #   echo "The following planners exist:"
        #   ls planners/
        #   exit 1
        # fi

        run $1 $2 $3 $4 $5 $6 $7 $8 $9
esac

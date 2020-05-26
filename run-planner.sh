#!/bin/bash

time_out=1800  # timeout in s

run()
{
    echo $1
    echo $2
    # $1: directory path,
    echo $1/results.csv
    echo "file,problem,planning_time,singlesoutcome_planning_call,alloutcome_planning_call,unsolvable_states,solvable,policy_length,plan_length" > $1/results.csv
    domain=$1/domain.pddl
    for problem in $1/*.pddl
    do
      case $problem in
          *"domain.pddl"* ) continue;;
      esac

      printf $problem

      start_time=`date +%s%N`
      output=`timeout $time_out nice -n 0 python3 main.py $domain $problem -d -s -c $2&`
      end_time=`date +%s%N`
      runingtime=$(((end_time-start_time)/1000000))
      echo ' ['$((runingtime/1000)).$((runingtime%1000))']'
      rm -fr /tmp/pyppddl/*
    done
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
        planner=$3

        if [ "$3" == "" ]; then
            planner="ff"
        fi

        if [ ! -f "planners/$planner" ]
        then
          echo "The planner '$planner' not found."
          echo "The following planners exist:"
          ls planners/
          exit 1
        fi

        domains=($2/*)
        for entry in ${domains[*]}; do
            run $entry $planner
        done
    ;;
    *)
        planner=$2

        if [ "$2" == "" ]; then
            planner="ff"
        fi

        if [ ! -f "planners/$planner" ]
        then
          echo "The planner '$planner' not found."
          echo "The following planners exist:"
          ls planners/
          exit 1
        fi

        run $1 $planner
esac

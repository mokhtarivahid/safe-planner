#!/bin/bash

time_out=600  # timeout in s

run()
{
    echo $1
    echo $2
    # $1: directory path,
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
    done
}

print_help()
{
        echo "Following options are allowed:"
        echo "./planner.sh <PATH> [<PLANNER>]       Solves problems in <PATH> using <PLANNER> (default <PLANNER>=ff)."
}

if [ $# -eq 0 ]; then
    print_help
    exit 1
fi

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

#!/bin/bash

time_out=600  # timeout in s

run()
{
    # $1: directory path,
    domain=$1/domain.pddl
    for problem in $1/*.pddl
    do
      case "$problem" in
          *domain* ) continue;;
          *sample* ) continue;;
      esac

      printf $problem

      start_time=`date +%s%N`
      output=`timeout $time_out nice -n 0 python3 main.py $domain $problem -d -s`
      end_time=`date +%s%N`
      runingtime=$(((end_time-start_time)/1000000))
      echo ' ['$((runingtime/1000)).$((runingtime%1000))']'
    done
}

print_help()
{
        echo "Following options are allowed:"
        echo " ./planner.sh <Path>       Solve problems in <Path>."
}

run $1


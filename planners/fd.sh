#!/bin/bash
##
# @Description: run the fd planner
##

# $(dirname $0)/fd/fast-downward.py --search-memory-limit 4G --sas-file /tmp/output.sas --plan-file /tmp/plan.txt $1 $2 --search "astar(lmcut())"

# $(dirname $0)/fd/fast-downward.py --search-memory-limit 4G --sas-file /tmp/output.sas --plan-file /tmp/plan.txt $1 $2 --evaluator "hcea=cea()" --search "lazy_greedy([hcea], preferred=[hcea])"

$(dirname $0)/fd/fast-downward.py --search-memory-limit 4G --sas-file /tmp/output.sas --plan-file /tmp/plan.txt $1 $2 --search "astar(add())"

# $(dirname $0)/fd/fast-downward.py --search-memory-limit 4G --sas-file /tmp/output.sas --plan-file /tmp/plan.txt $1 $2 --evaluator "hff=ff()" --evaluator "hcea=cea()" --search "lazy_greedy([hff, hcea], preferred=[hff, hcea])"
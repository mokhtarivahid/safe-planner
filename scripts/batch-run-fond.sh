#!/bin/bash
##
# @Description: run the planner in all fond benchmarks
##

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$script_dir" || exit 1

# ```bash
# # run Safe-Planner in batch for all FOND domains in dual replanning mode 
# # using ff and m planners in both single-outcome (safe-planner algorithm) 
# # and all-outcome (ndp2 algorithm)
# ./batch-run-fond.sh 
# ```


declare -a domains=("../benchmarks/fond-domains/acrobatics"
                    "../benchmarks/fond-domains/beam-walk -r 1"
                    "../benchmarks/fond-domains/blocksworld"
                    "../benchmarks/fond-domains/doors -r 1"
                    "../benchmarks/fond-domains/elevators"
                    "../benchmarks/fond-domains/ex-blocksworld"
                    "../benchmarks/fond-domains/first-responders"
                    "../benchmarks/fond-domains/forest"
                    "../benchmarks/fond-domains/islands -r 1"
                    "../benchmarks/fond-domains/miner -r 1"
                    "../benchmarks/fond-domains/tireworld"
                    "../benchmarks/fond-domains/tireworld-spiky"
                    "../benchmarks/fond-domains/tireworld-truck"
                    "../benchmarks/fond-domains/triangle-tireworld"
                    "../benchmarks/fond-domains/zenotravel")

# different planning configurations
declare -a configurations=("-c ff m" "-c ff m -a")

# run on fond domains in 'dom' array
for i in "${domains[@]}"; do
    for j in "${configurations[@]}"; do
        ./batch-run.sh $i $j
        sleep 1
        echo
    done
done

# run on 'faults' domain
for j in "${configurations[@]}"; do
    ./batch-run-faults.sh -r 1 $j
    sleep 1
    echo
done

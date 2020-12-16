#!/bin/bash
##
# @Description: run the planner in all fond benchmarks
##

declare -a domains=("benchmarks/fond-domains/acrobatics"
                    "benchmarks/fond-domains/beam-walk -r"
                    "benchmarks/fond-domains/blocksworld"
                    "benchmarks/fond-domains/doors -r"
                    "benchmarks/fond-domains/elevators"
                    "benchmarks/fond-domains/ex-blocksworld"
                    "benchmarks/fond-domains/first-responders"
                    "benchmarks/fond-domains/forest"
                    "benchmarks/fond-domains/islands -r"
                    "benchmarks/fond-domains/miner -r"
                    "benchmarks/fond-domains/tireworld"
                    "benchmarks/fond-domains/tireworld-spiky"
                    "benchmarks/fond-domains/tireworld-truck"
                    "benchmarks/fond-domains/triangle-tireworld"
                    "benchmarks/fond-domains/zenotravel")

# different planning configurations
declare -a configurations=("-c ff m" "-c ff m -a")

# run on fond domains in 'dom' array
for i in "${domains[@]}"; do
    for j in "${configurations[@]}"; do
        ./run.sh $i $j
        sleep 1
        echo
    done
done

# run on 'faults' domain
for j in "${configurations[@]}"; do
    ./run-faults.sh -r $j
    sleep 1
    echo
done

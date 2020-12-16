#!/usr/bin/python
## libraries to install
# sudo apt-get install -y python3-pip
# pip3 install pandas

import sys, os
from collections import OrderedDict, defaultdict

if len(sys.argv) > 1 and \
    ( sys.argv[1] == '-h' or sys.argv[1] == '--help'):
    print("usage: python3 table.py [-o] [-h]")
    print("optional arguments:")
    print("  -h, --help            show this help message and exit")
    print("  -o, --output          write the output into csv files in 'output' directory")
    exit(1)

import pandas as pd
import numpy as np

ex_results = ['SP$_{FD}$.csv', 'SP$_{FF}$.csv', 'SP$_{M}$.csv', 'SP$_{LPG-TD}$.csv']
# ex_results = ['PRP.csv', 'NDP2.csv', 'SP.csv', 'SP$_{FD}$.csv', 'SP$_{FF}$.csv', 'SP$_{M}$.csv', 'SP$_{LPG-TD}$.csv']

# store the average results for every domain and every planner
avg_results = OrderedDict()

# total problems solved
total_solved_problems = defaultdict(int)
total_unsolved_problems = defaultdict(int)
total_proved_unsolvable = defaultdict(int)

# load a list of domains (directories)
domains = sorted([d for d in os.listdir(r'.') if os.path.isdir(d) and not d == 'output'])

# read the result of planners in every domain
for domain in domains:
    print(domain)

    data = OrderedDict()
    data['Metric'] = [ \
        'avg. time', \
        'avg. policy size', \
        'no. of solved problems', \
        'no. of unsolvable problems', \
        'no. of proved unsolvable problems', \
        'avg. planning call', \
        # 'avg. planning call (alloutcome)', \
        'avg. unsolvable states' ]

    for planner in os.listdir(domain):
        # ignore dummy files remained from libre office
        if planner.startswith('.~'): continue

        # exclude some files
        # if planner in ex_results: continue

        # skip PRP and SAT
        # if not planner in ['SP.csv', 'NDP2.csv']: continue
        # if not "$" in planner: continue

        # load the csv file and convert nan to '0'
        df = pd.read_csv(domain+'/'+planner,header=0).fillna(0)
        # print(df)

        # refine the name of the file (planner)
        planner = os.path.splitext(os.path.basename(planner))[0].replace('$','').upper()
        # print(planner)

        # number of problems that either solved or proved unsolvable within 30 minutes
        div = len([x for x in df.problem.tolist() if isinstance(x, str) and x != '0'])

        # compute the average of the following columns
        data[planner] = [ \
            sum(df.planning_time.tolist()) / div if div > 0 else 0, \
            sum(df.policy_length.tolist()) / div if div > 0 else 0, \
            sum(df.solvable.tolist()), \
            len(df.file.tolist())-div, \
            div-sum(df.solvable.tolist()), \
            sum(df.singlesoutcome_planning_call.tolist()) / div if div > 0 else 0, \
            # sum(df.alloutcome_planning_call.tolist()) / div, \
            sum(df.unsolvable_states.tolist()) / div if div > 0 else 0]

        total_solved_problems[planner] += sum(df.solvable.tolist())
        total_unsolved_problems[planner] += len(df.file.tolist())-div
        total_proved_unsolvable[planner] += div-sum(df.solvable.tolist())

    # Create DataFrame
    df = pd.DataFrame(data)

    # round the values into int
    for planner in df.columns.tolist()[1:]:
        df[planner] = np.round(df[planner]).astype('Int64')

    # add the results for the current domain
    avg_results[domain] = df

# create output directory to store results
if not os.path.exists('output'):
    os.makedirs('output')

# print the output and store them into csv files
for domain, result in avg_results.items():     
    print(domain.upper())
    print(result)
    if len(sys.argv) > 1 and sys.argv[1] == '-o':
        with open('output/%s.csv'%domain, 'w') as file_object:
            # skip header
            file_object.write(result.to_csv(index=False))
    print('----------------------------------------')

print('\nTOTAL NUMBER OF SOLVED PROBLEMS')
print('PLANNER         : SOLVED : UNSOLVED : PROVED UNSOLVABLE : TOTAL')
print('---------------------------------------------------------------')
for planner, solved in total_solved_problems.items():
    print('{:<15s} : {:<8} {:<10} {:<19} {:<8}'.format(planner.upper(), \
        int(solved), int(total_unsolved_problems[planner]), int(total_proved_unsolvable[planner]), \
        int(solved) + int(total_unsolved_problems[planner]) + int(total_proved_unsolvable[planner])))


# # print the output and store them into csv files
# for domain, results in avg_results.items():     
#     print(domain.upper())
#     # for name, data in results.iteritems():
#     #     print(name, data.values)
#     # iterating over rows using iterrows() function  
#     print(results.keys().values.tolist()[1:])
#     for i, j in results.iterrows():
#         if 'no. of solved problems' in j.values.tolist()[0]:
#             # print(j.values.tolist()[0])
#             # print(j.keys().values.tolist()[1:])
#             print(j.values.tolist()[1:])
#             print() 

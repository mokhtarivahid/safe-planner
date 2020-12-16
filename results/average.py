#!/usr/bin/python
## libraries to install
# sudo apt-get install -y python3-pip
# pip3 install pandas

import sys, os
from collections import OrderedDict

if len(sys.argv) > 1 and \
    ( sys.argv[1] == '-h' or sys.argv[1] == '--help'):
    print("usage: python3 table.py [-o] [-h]")
    print("optional arguments:")
    print("  -h, --help            show this help message and exit")
    print("  -o, --output          write the output into csv files in 'output' directory")
    exit(1)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

COLOR = { 0 : 'navy',
          1 : 'skyblue',
          2 : 'darkcyan',
          3 : 'black' }

# store the average results for every domain and every planner
avg_results = OrderedDict()

# load a list of domains (directories)
domains = sorted([d for d in os.listdir(r'.') if os.path.isdir(d) and not d == 'output'])

# read the result of planners in every domain
for domain in domains:
    print(domain)

    for planner in os.listdir(domain):

        # skip PRP and SAT
        if not planner in ['SP.csv', 'NDP2.csv']: continue

        # load the csv file and convert nan to '0'
        df = pd.read_csv(domain+'/'+planner,header=0).fillna(0)

        # refine the name of the file (planner)
        planner = os.path.splitext(os.path.basename(planner))[0].replace('_','+').upper()
        # print(planner)

        # set default value as dict
        if planner not in avg_results:
            avg_results[planner] = OrderedDict()

        # number of problems that either solved or proved unsolvable within 30 minutes
        div = len([x for x in df.problem.tolist() if isinstance(x, str) and x != '0'])

        # compute the average of the following columns
        avg_results[planner][domain] = { \
            'planning_time (s)' : sum(df.planning_time.tolist()) / div if div > 0 else 0, \
            'policy_length' : sum(df.policy_length.tolist()) / div if div > 0 else 0, \
            # 'solvable' : sum(df.solvable.tolist()), \
            'singlesoutcome_planning_call' : sum(df.singlesoutcome_planning_call.tolist()) / div if div > 0 else 0, \
            # 'alloutcome_planning_call' : sum(df.alloutcome_planning_call.tolist()) / div, \
            'unsolvable_states' : sum(df.unsolvable_states.tolist()) / div if div > 0 else 0}


# Create DataFrame
# df = pd.DataFrame(avg_results)

# # round the values into int
# for planner in df.columns.tolist():
#     df[planner] = np.round(df[planner]).astype('Int64')

# # add the results for the current domain
# avg_results[domain] = df

# print(avg_results)

# find metrics 
metrics = []
for planner, results in avg_results.items():
    for domain, result in results.items():
        metrics = list(sorted(result.keys()))
        break
    break

# create DataFrames for metrics for every planner
df_results = OrderedDict()
for metric in metrics:
    data = OrderedDict()
    for planner, results in avg_results.items():
        data['domain'] = list(results.keys())
        data[planner] = [result[metric] for domain, result in results.items()]

    # create DataFrame
    df = pd.DataFrame(data).round(1)
    df_results[metric] = df


# create plots

# size of the plot
(ROWS, COLS) = (2, 2)

fig, axs = plt.subplots(ncols=COLS, nrows=ROWS, figsize=(16,8))
# fig.tight_layout(pad=3.0)
# plt.subplots_adjust(hspace=0.1)

for d, (metric, df) in enumerate(df_results.items()):
    i = int(d/(ROWS))
    j = d%(ROWS)

    print(metric.upper(), (i, j))
    print(df)

    dim = len(df)
    w = 6
    dimw = w / dim
    x = np.arange(len(df))

    for k, planner in enumerate(df.columns[1:]):
        axs[i,j].bar(x=x + k * dimw, height=df[planner], width=dimw, label=(r'%s'%planner), color=COLOR[k%(len(COLOR))])

    axs[i,j].legend(loc='best', frameon=False, fontsize=10)
    print(metric.split('_')[-2:])
    axs[i,j].set_ylabel(' '.join(metric.split('_')[-2:]).title())

    axs[i,j].set_xticks(x + dimw / 2)
    axs[i,j].set_xticklabels(df['domain'], rotation=45)

    axs[i,j].set_yticks(df[planner].values.tolist())
    axs[i,j].set_yticklabels(df[planner])

    axs[i,j].set_yscale('log')
    axs[i,j].yaxis.set_major_formatter(ticker.ScalarFormatter())

fig.tight_layout(pad=0.0)
fig.savefig('average.pdf', bbox_inches='tight')

# plt.show()

# data = defaultdict(dict)

# # create output directory to store results
# if not os.path.exists('output'):
#     os.makedirs('output')

# # print the output and store them into csv files
# for domain, result in avg_results.items():
#     print(domain.upper())
#     print(result, len(result))
#     if len(sys.argv) > 1 and sys.argv[1] == '-o':
#         with open('output/%s.csv'%domain, 'w') as file_object:
#             # skip header
#             file_object.write(result.to_csv(index=False))
#     print('----------------------------------------')

# crop the output pdf file
os.system('pdfcrop average.pdf average.pdf')


#!/usr/bin/python
## libraries to install
# sudo apt-get install -y python3-pip
# pip3 install pandas

import sys, os

if len(sys.argv) > 1 and \
    ( sys.argv[1] == '-h' or sys.argv[1] == '--help'):
    print("usage: python3 table.py [-o] [-h]")
    print("optional arguments:")
    print("  -h, --help            show this help message and exit")
    exit(1)

from collections import OrderedDict, defaultdict
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

ex_results = ['SP$_{M}$.csv', 'SP$_{FD}$.csv', 'SP$_{PROBE}$.csv', 'SP$_{LPG-TD}$.csv']
# ex_results = ['PRP.csv', 'NDP2.csv', 'SP.csv', 'SP$_{FD}$.csv', 'SP$_{FF}$.csv', 'SP$_{M}$.csv', 'SP$_{LPG-TD}$.csv']

# load a list of domains (directories)
domains = sorted([d for d in os.listdir(r'.') if os.path.isdir(d) and not d == 'output'])

# store planning time for all problems (only solvables)
planning_time = defaultdict(list)

# read the result of planners in every domain
for domain in domains:
    print(domain)

    for planner in sorted(os.listdir(domain)):
        # ignore dummy files remained from libre office
        if planner.startswith('.~'): continue

        # exclude some files
        if planner in ex_results: continue

        # load the csv file and convert nan to '0'
        df = pd.read_csv(domain+'/'+planner,header=0).fillna(0)
        # print(df)

        # refine the name of the file (planner)
        planner = os.path.splitext(os.path.basename(planner))[0].replace('$','').upper()
        if planner == 'NDP2': planner = 'NDP2_{FF+M}'
        if planner == 'SP': planner = 'SP_{FF+M}'
        # print(planner)

        # append the planning time of solvable problems
        planning_time[planner] += df.loc[df['solvable'] == 1].planning_time.tolist()

fig, ax = plt.subplots()

ax.set(xlabel='number of solved problems', ylabel='time (s)',
       title='IPC FOND Domains')

ax.set_yscale('symlog')

for planner, planning_time in planning_time.items():
    line, = ax.plot(sorted(planning_time))
    line.set_label(planner)

ax.legend(loc='best', frameon=False, fontsize=8)

# plt.gca().invert_yaxis()

fig.savefig('cactus.pdf', bbox_inches='tight')

# crop the output pdf file
os.system('pdfcrop cactus.pdf cactus.pdf')


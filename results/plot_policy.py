#!/usr/bin/python
## libraries to install
# sudo apt-get install -y python3-pip
# pip3 install matplotlib
# pip3 install pandas

import sys, os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# plt.style.use('classic')

# size of the plot
(ROWS, COLS) = (4, 4)

in_sat_results = ['doors', 'elevators', 'ex-blocksworld', 'islands', 'miner', 'tireworld', 'tireworld-spiky', 'tireworld-truck', 'triangle-tireworld', 'zenotravel']
ex_results = ['SP$_{FD}$.csv', 'SP$_{FF}$.csv', 'SP$_{M}$.csv', 'SP$_{LPG-TD}$.csv']

LN_STYLE = { 0 : ['-','x'], 
             2 : ['-','+'],
             4 : [':','2'],
             3 : ['-.',','],
             1 : ['-','.'] }

fig, axs = plt.subplots(ncols=COLS, nrows=ROWS, figsize=(32,18))
# fig.tight_layout(pad=2.0)
plt.subplots_adjust(hspace=0.1)
# plt.yscale('log')

# load a list of domains (directories)
domains = sorted([d for d in os.listdir(r'.') if os.path.isdir(d) and not d == 'output'])

for d, domain in enumerate(domains):
    i = int(d/(ROWS))
    j = d%(ROWS)
    print(domain, (i, j))

    probs_n = 0

    for r, result in enumerate(os.listdir(domain)):

        if result in ex_results: continue

        planner = os.path.splitext(os.path.basename(result))[0].replace('_','+')

        df = pd.read_csv(domain+'/'+result,header=0)
        # print(df)

        # convert unsolvable problems to 'nan'
        (files, problems) = (df.file.copy(), df.problem.copy())
        for index, value in df['solvable'].items():
            if value == 0: 
                df.loc[index] = float('nan')
        (df.file, df.problem) = (files, problems)
        # df.replace({'file':float('nan'), 'file':float('nan')}, '', inplace=True)
        # print(df)
        x =r%(len(LN_STYLE))
        if not planner == 'SAT':
            axs[i, j].plot(df['file'], df['policy_length'], linestyle=LN_STYLE[x][0], marker=LN_STYLE[x][1], markerfacecolor='none', label=(r'%s'%planner), markersize=16, linewidth=3)
        elif planner == 'SAT' and domain in in_sat_results:
            axs[i, j].plot(df['file'], df['policy_length'], linestyle=LN_STYLE[x][0], marker=LN_STYLE[x][1], markerfacecolor='none', label=(r'%s'%planner), markersize=16, linewidth=3)

        if probs_n < len(df['file']):
            probs_n = len(df['file'])

    step = 1
    if len(df['file']) > 90:
            step = 6
    elif len(df['file']) > 60:
            step = 5
    elif len(df['file']) > 40:
            step = 4
    elif len(df['file']) > 30:
            step = 3
    elif len(df['file']) > 20:
            step = 2

    x_idxs = list(range(probs_n))[0::step] 
    x_lbls = list(range(1,probs_n+1))[0::step] 
    if (len(range(probs_n))-x_lbls[-2])*3/5 >= step:
        x_idxs.append(len(range(probs_n))-1)
        x_lbls.append(len(range(probs_n)))
    else:
        x_idxs[-1] = len(range(probs_n))-1
        x_lbls[-1] = len(range(probs_n))

    axs[i, j].set_xticks(x_idxs)
    axs[i, j].set_xticklabels(x_lbls, fontsize=16)
    # if i == 1:
    #     axs[i, j].set_xlabel('problems', fontsize=18)

    axs[i, j].tick_params(axis="y", labelsize=16)
    # if j == 0:
    #     axs[i, j].set_ylabel('planning time (s)', fontsize=18)

    axs[i, j].legend(loc='best', frameon=False, fontsize=18)

    axs[i, j].set_title(domain.title(), 
                        position=(0.5, 0.92), 
                        fontdict={'family': 'serif', 
                                            # 'color' : 'darkblue',
                                            # 'weight': 'bold',
                                            'size': 18})
    # axs[i, j].xlabel('problems', fontsize=18)
    axs[i, j].set_yscale("log")
    axs[i, j].yaxis.set_major_formatter(ticker.ScalarFormatter())

fig.text(-0.005, 0.5, 'Policy Size', fontsize=18, va='center', rotation='vertical')
fig.text(0.5, -0.01, 'Problems', fontsize=18, ha='center')

fig.tight_layout(pad=.1)
fig.savefig('plot_policy.pdf', bbox_inches='tight')

# plt.show()

# crop the output pdf file
os.system('pdfcrop plot_policy.pdf plot_policy.pdf')

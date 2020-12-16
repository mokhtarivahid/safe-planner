#!/usr/bin/env python

import argparse
import os, time
import json
from collections import OrderedDict

def parse():
    usage = 'python3 main.py <DOMAIN> <PROBLEM> [<PLANNER>] [-v | --verbose N] [-h | --help]'
    description = "Safe-Planner is a non-deterministic planner for PPDDL."
    parser = argparse.ArgumentParser(usage=usage, description=description)

    parser.add_argument('domain',  type=str, help='path to PDDL domain file')
    parser.add_argument('problem', type=str, help='path to PDDL problem file')
    parser.add_argument("planner", type=str, nargs='?', const=1, 
        help="external planner: ff, m, optic, vhpop, ... (default=ff)", default="ff")
    # parser.add_argument("-v", "--verbose", help="increase output verbosity", 
    #     action="store_true")
    parser.add_argument("-v", "--verbose", default=0, type=int, 
        help="increase output verbosity: 0 (nothing), 1 (high-level), 2 (external planners outputs) (default=0)", )

    return parser.parse_args()


###############################################################################
def gen_json_plan(plan, json_file=None):
    '''transforms a plan into a json object (OrderedDict) and stores it in a 
       file and return the json object and path to the json file
    '''
    plan_json = OrderedDict()
    for level, step in plan.items():

        plan_json.setdefault('plan', []).append('step{}'.format(str(level)))

        step_json = OrderedDict()

        if step is None or step is 'GOAL': 
          # plan_json.setdefault('step_descriptions', []).append(dict( { 'step{}'.format(str(level)) : \
          #   dict({'actions':[], 'outcomes':[dict({'condition':[], 'next':''})]}) } ))
          step_json['actions'] = []
          step_json['outcomes'] = [dict({'condition':[], 'next':''})]
          
        else:
          (actions, outcomes) = step

          for i, action in enumerate(actions):
              step_json.setdefault('actions',[]).append( {'name' : action.sig[0], 'arguments' : action.sig[1:]} )

          for (conditions, jump) in outcomes:
              if len(conditions) > 0:
                  step_json.setdefault('outcomes',[]).append(\
                      dict({'condition':['({0})'.format(' '.join(map(str, cnd))) for cnd in conditions[0]], \
                        'next':'step{}'.format(str(jump))}))
              else:
                  step_json.setdefault('outcomes',[]).append(dict({'condition':[], \
                    'next':'step{}'.format(str(jump))}))

        plan_json['step{}'.format(str(level))] = step_json
        # plan_json.setdefault('step_descriptions', []).append(dict( {'step{}'.format(str(level)) : step_json} ))

    plan_json_str = json.dumps(plan_json, indent=4)
    # print(plan_json_str)

    # create a json file
    if json_file == None:
        if not os.path.exists("/tmp/safe-planner/"):
            os.makedirs("/tmp/safe-planner/")
        json_file = "/tmp/safe-planner/prob"+str(int(time.time()*1000000))+".json"
    else:
        json_file = '{}.json'.format(os.path.splitext(json_file)[0])

    with open(json_file, 'w') as outfile:
        json.dump(json.loads(plan_json_str, object_pairs_hook=OrderedDict), outfile, sort_keys=False, indent=4)

    return json_file, plan_json


###############################################################################
if __name__ == '__main__':

    import color
    import planner

    args = parse()

    policy = planner.Planner(args.domain, args.problem, args.planner, args.verbose)

    plan = policy.plan()
    policy.print_plan()

    json_file_path, plan_json = gen_json_plan(plan, args.problem)

    print(color.fg_yellow('-- json plan object\n') + str(plan_json))
    print(color.fg_yellow('-- json file\n') +str(json_file_path))

    # with open(json_file_path) as json_file:
    #     plan_json = json.load(json_file)

    # print(plan_json)

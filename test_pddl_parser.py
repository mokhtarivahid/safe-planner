
import argparse

from color import fg_green, fg_red, fg_yellow, fg_blue, fg_voilet, fg_beige, bg_voilet, bg_beige, bg_yellow
from planner import Planner
from pddlparser import PDDLParser


def parse():
    usage = 'python3 main.py <DOMAIN> <PROBLEM>'
    description = "TEST THE PDDL PARSER."
    parser = argparse.ArgumentParser(usage=usage, description=description)

    parser.add_argument('domain',  type=str, help='path to a PDDL domain file')
    # parser.add_argument('problem', type=str, help='path to a PDDL problem file')

    return parser.parse_args()



if __name__ == '__main__':

    args = parse()

    domain = PDDLParser.parse(args.domain)
    # problem = PDDLParser.parse(args.problem)

    print(domain.__str__(pddl=True))
    # print(problem)
    # for p in domain[5]:
    #     for d in p:
    #         print(d)
    #         print()
    #     print('-----------')

    # print(bg_yellow('@ pddl'))
    # print(domain.__str__(pddl=True))
    # print(bg_yellow('@ pddl'))
    # print(problem.__str__(pddl=True))

#!/usr/bin/env python3

import argparse

from color import fg_green, fg_red, fg_yellow, fg_blue, fg_voilet, fg_beige, bg_voilet, bg_beige, bg_yellow
from planner import Planner, mergeDict
from pddlparser import PDDLParser
from pddl import pddl, to_pddl


def parse():
    usage = 'python3 main.py <DOMAIN> <PROBLEM>'
    description = "TEST THE PDDL PARSER."
    parser = argparse.ArgumentParser(usage=usage, description=description)

    parser.add_argument('domain',  type=str, help='path to a PDDL domain file')
    parser.add_argument('problem', type=str, help='path to a PDDL problem file')

    return parser.parse_args()


if __name__ == '__main__':

    args = parse()

    domain = PDDLParser.parse(args.domain)
    problem = PDDLParser.parse(args.problem)
    problem.objects = mergeDict(problem.objects, domain.constants)

    print(problem)
    print(domain)
    print(to_pddl(problem))
    print(to_pddl(domain))
    print(pddl(problem))
    print(pddl(domain))

#!/usr/bin/env python3

import argparse

from color import fg_green, fg_red, fg_yellow, fg_blue, fg_voilet, fg_beige, bg_voilet, bg_beige, bg_yellow
from planner import Planner, mergeDict
from pddlparser import PDDLParser
from pddl import pddl, to_pddl


def parse():
    usage = 'python3 main.py <DOMAIN> [<PROBLEM>] [-a] [-h]'
    description = "TEST THE PDDL PARSER."
    parser = argparse.ArgumentParser(usage=usage, description=description)

    parser.add_argument('domain',  nargs='?', type=str, help='path to a PDDL domain file')
    parser.add_argument('problem', nargs='?', type=str, help='path to a PDDL problem file')
    parser.add_argument("-a", "--all", help="print out all outputs", action="store_true")

    return parser


if __name__ == '__main__':

    parser = parse()
    args = parser.parse_args()

    if args.domain is None and args.problem is None:
        parser.print_help()
        exit()

    ## if only one arg (domain) is given
    if args.problem is None:
        domain = PDDLParser.parse(args.domain)

        ## if problem is also in the file
        if type(domain) == tuple:
            domain, problem = domain[0], domain[1]
            problem.objects = mergeDict(problem.objects, domain.constants)
        else:
            problem = None
    ## if both args (domain, problem) are given
    else:
        domain = PDDLParser.parse(args.domain)
        problem = PDDLParser.parse(args.problem)
        problem.objects = mergeDict(problem.objects, domain.constants)


    ## print out in string
    if args.all: 
        print(fg_yellow('-- domain in string'))
        print(domain)
    if args.all and problem is not None: 
        print(fg_yellow('-- problem in string'))
        print(problem)

    ## print out in pddl
    print(fg_yellow('-- domain in pddl '))
    print(to_pddl(domain))
    if problem is not None: 
        print(fg_yellow('-- problem in pddl '))
        print(to_pddl(problem))

    ## print out pddl files
    if args.all: 
        print(fg_yellow('-- domain pddl file: ') + pddl(domain))
    if args.all and problem is not None: 
        print(fg_yellow('-- problem pddl file: ') + pddl(problem))

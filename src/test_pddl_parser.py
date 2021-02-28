#!/usr/bin/env python

import argparse

import color
import planner
import pddlparser
import pddl

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
        domain = pddlparser.PDDLParser.parse(args.domain)

        ## if problem is also in the file
        if type(domain) == tuple:
            domain, problem = domain[0], domain[1]
            problem.initial_state.objects = planner.mergeDict(problem.initial_state.objects, domain.constants)
        else:
            problem = None
    ## if both args (domain, problem) are given
    else:
        domain = pddlparser.PDDLParser.parse(args.domain)
        problem = pddlparser.PDDLParser.parse(args.problem)
        problem.initial_state.objects = planner.mergeDict(problem.initial_state.objects, domain.constants)


    ## print out in string
    if args.all: 
        print(color.fg_yellow('-- domain in string'))
        print(domain)
    if args.all and problem is not None: 
        print(color.fg_yellow('-- problem in string'))
        print(problem)

    ## print out in pddl
    print(color.fg_yellow('-- domain in pddl '))
    print(pddl.to_pddl(domain))
    if problem is not None: 
        print(color.fg_yellow('-- problem in pddl '))
        print(pddl.to_pddl(problem))

    ## print out pddl files
    if args.all: 
        print(color.fg_yellow('-- domain pddl file: ') + pddl.pddl(domain))
    if args.all and problem is not None: 
        print(color.fg_yellow('-- problem pddl file: ') + pddl.pddl(problem))

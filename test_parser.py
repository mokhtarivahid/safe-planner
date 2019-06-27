
import argparse

from color import fg_green, fg_red, fg_yellow, fg_blue, fg_voilet, fg_beige, bg_voilet, bg_beige, bg_yellow
from planner import Planner
from pddlparser import PDDLParser


def parse():
    usage = 'python3 main.py <DOMAIN> <PROBLEM> [<PLANNER>] [-v | --verbose]'
    description = "pypddl is a probabilistic planner."
    parser = argparse.ArgumentParser(usage=usage, description=description)

    parser.add_argument('domain',  type=str, help='path to PDDL domain file')
    parser.add_argument('problem', type=str, help='path to PDDL problem file')
    parser.add_argument("planner", type=str, nargs='?', const=1, 
        help="external planner: ff, m, optic, vhpop, ... (default=ff)", default="ff")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", 
        action="store_true")

    return parser.parse_args()



if __name__ == '__main__':

    args = parse()

    domain = PDDLParser.parse(args.domain)
    problem = PDDLParser.parse(args.problem)

    print(domain)
    print(problem)

    print(bg_yellow('@ pddl'))
    print(domain.__str__(pddl=True))
    print(bg_yellow('@ pddl'))
    print(problem.__str__(pddl=True))

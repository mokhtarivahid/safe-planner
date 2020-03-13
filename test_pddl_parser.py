
import argparse

from color import fg_green, fg_red, fg_yellow, fg_blue, fg_voilet, fg_beige, bg_voilet, bg_beige, bg_yellow
from planner import Planner, mergeDict
from pddlparser import PDDLParser


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
    # print(problem.objects)

    # print(problem.goals)

    # print(domain.__str__(pddl=True))
    # print(problem.__str__(pddl=True))
    # print(problem)
    # for p in domain[5]:
    #     for d in p:
    #         print(d)
    #         print()
    #     print('-----------')

    # print(bg_yellow('@ pddl'))
    # print(domain.__str__(pddl=True))
    # print(bg_yellow('@ pddl'))
    
    # grounded_actions = domain.ground_actions(problem.objects)
    # print(len(grounded_actions))
    act = domain.ground(('pickup-empty','left-arm','object1','obj1_gpt','table1'))
    # print(act.when_effects)
    # print(act.pos_preconditions, act.neg_preconditions)
    if problem.initial_state.is_true(act.pos_preconditions, act.neg_preconditions):
        # print(act.__str__(body=True))
        new = problem.initial_state.apply(act)
        # print(set(problem.initial_state.predicates))
        # print()
        # print(set(new.predicates))
        print(set(problem.initial_state.predicates) - set(new.predicates))
        print(set(new.predicates) - set(problem.initial_state.predicates))
    # for action in grounded_actions:
    #     if problem.initial_state.is_true(action.pos_preconditions, action.neg_preconditions):
    #         print(action)
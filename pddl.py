"""
functions for creating PDDL-like problem and domain files for planning
"""
import os, time

from domain import Domain, Action, Precondition, Effect
from problem import Problem, State

def to_pddl(object, state=None, goals=None):
    """
    Return the given object as a pddl string
    @arg object : a given object (Precondition/Effect/Action/Domain/Problem)
    @arg state : a given initial state (default is the problem initial state)
    @arg goal : a given problem goal (default is the problem goal)
    """
    ## translate a Precondition object into a pddl string
    if type(object) is Precondition:
        precond_str = '(and'
        for pre in object.literals:
            if pre[0] == -1:
                precond_str += ' (not ({0}))'.format(' '.join(map(str, pre[1:][0])))
            else:
                precond_str += ' ({0})'.format(' '.join(map(str, pre)))
        ## universal-preconditions
        for uni in object.universal:
            types, variables = zip(*uni[0])
            varlist = ' '.join(['%s - %s' % pair for pair in zip(variables, types)])
            precond_str += '\n             (forall ({}) {})'.format(varlist,literals_to_pddl(uni[1]))
        ## existential-preconditions
        for ext in object.existential:
            types, variables = zip(*ext[0])
            varlist = ' '.join(['%s - %s' % pair for pair in zip(variables, types)])
            precond_str += '\n             (exists ({}) {})'.format(varlist,literals_to_pddl(uni[1]))
        precond_str += ')'
        return precond_str

    ## translate an Effect object into a pddl string
    elif type(object) is Effect:
        (lit_str, for_str, whn_str) = (str(), str(), str())
        for pre in object.literals:
            if pre[0] == -1:
                lit_str += '(not ({0}))'.format(' '.join(map(str, pre[1:][0])))
            else:
                lit_str += '({0})'.format(' '.join(map(str, pre)))
        for uni in object.forall:
            types, variables = zip(*uni[0])
            varlist = ' '.join(['%s - %s' % pair for pair in zip(variables, types)])
            for_str += '(forall ({}) {})'.format(varlist,literals_to_pddl(uni[1]))
        for uni in object.when:
            whn_str += '(when {} {})'.format(literals_to_pddl(uni[0]),literals_to_pddl(uni[1]))
        return (lit_str, for_str, whn_str)

    ## translate a Action object into a pddl string
    elif type(object) is Action:
        arglist   = ' '.join(['%s - %s' % pair for pair in zip(object.arg_names, object.types)])
        pddl_str  = '\n  (:action {0}\n   :parameters ({1})'.format(object.name, arglist)
        pddl_str += '\n   :precondition\n        {}'.format(to_pddl(object.preconditions))
        pddl_str += '\n   :effect\n        (and {}'.format('\n             '.join(filter(None,to_pddl(object.effects))))
        for probabilistic in object.probabilistic:
            prob_lst = list()
            for prob in probabilistic:
                prob_str = to_pddl(prob[1])
                prob_lst.append('{} (and {}{}{})'.format(str(prob[0]), prob_str[0], prob_str[1], prob_str[2]))
            pddl_str += '\n             (probabilistic {})'.format('\n                            '.join(map(str, prob_lst)))
        for oneof in object.oneof:
            oneof_lst = list()
            for one in oneof:
                oneof_str = to_pddl(one)
                oneof_lst.append('(and {}{}{})'.format(oneof_str[0], oneof_str[1], oneof_str[2]))
            pddl_str += '\n             (oneof {})'.format('\n                    '.join(map(str, oneof_lst)))
        pddl_str += ')'
        pddl_str += ')\n'
        return pddl_str

    ## translate a Domain object into a pddl string
    elif type(object) is Domain:
        pddl_str  = '(define (domain {0})\n\n'.format(object.name)
        pddl_str += '  (:requirements {0})\n\n'.format(' '.join(object.requirements))
        if len(object.types) > 0:
            typed_str = '\n          '.join(['{} - {}'.format(' '.join(map(str,v)), k) for k,v in object.types.items() if v])
            untyped_str = ' '.join([k for k,v in object.types.items() if not v])
            pddl_str += '  (:types {} {})\n\n'.format(typed_str,untyped_str)
        if len(object.constants) > 0:
            pddl_str += '  (:constants\n'
            for _type in sorted(object.constants.keys())[:-1]:
                pddl_str += '        {0} - {1}\n'.format(' '.join(sorted(object.constants[_type])), _type)
            _type = sorted(object.constants.keys())[-1]
            pddl_str += '        {0} - {1})\n\n'.format(' '.join(sorted(object.constants[_type])), _type)
        pddl_str += '  (:predicates'
        for predicate in object.predicates:
            pddl_str += '\n        ({0} {1})'.format(predicate[0],
                ' '.join(' - '.join(reversed(p)) for p in predicate[1:]))
        pddl_str += ')\n'
        for action in object.actions:
            pddl_str += to_pddl(action)
        pddl_str += ')\n'
        return pddl_str

    ## translate a Domain object into a pddl string
    elif type(object) is Problem:
        if state == None:
            state = object.initial_state

        if goals == None:
            goals = object.goals

        pddl_str  = '(define (problem {0})\n'.format(object.problem)
        pddl_str += '  (:domain {0})\n'.format(object.domain)
        if len(object.objects) > 0:
            pddl_str += '  (:objects \n'
            for _type in sorted(object.objects.keys())[:-1]:
                pddl_str += '\t\t{0} - {1}\n'.format(' '.join(sorted(object.objects[_type])), _type)
            _type = sorted(object.objects.keys())[-1]
            pddl_str += '\t\t{0} - {1})\n'.format(' '.join(sorted(object.objects[_type])), _type)
        pddl_str += '  (:init'
        for predicate in state.predicates:
            pddl_str += '\n\t\t({0})'.format(' '.join(map(str, predicate)))
        pddl_str += ')\n'
        pddl_str += '  (:goal (and'
        for predicate in goals:
            pddl_str += '\n\t\t({0})'.format(' '.join(map(str, predicate)))
        pddl_str += ')))\n'
        return pddl_str


def pddl(object, state=None, goals=None):
    """
    create a pddl file of the given object and return its path as a string
    @arg object : a given object (Precondition/Effect/Action/Domain/Problem)
    @arg state : a given initial state (default is the problem initial state)
    @arg goal : a given problem goal (default is the problem goal)
    """
    if not os.path.exists("/tmp/pyddl/"):
        os.makedirs("/tmp/pyddl/")
    pddl = "/tmp/pyddl/prob"+str(int(time.time()*1000000))+".pddl"
    with open(pddl, 'w') as f:
        f.write(to_pddl(object, state=state, goals=goals))
        f.close()
    return pddl

## a function to convert a list of literals into a pddl string
def literals_to_pddl(literal_lst):

    def literal_to_pddl(literal):
        if literal[0] == -1:
            return '(not ({0}))'.format(' '.join(map(str, literal[1:][0])))
        return '({0})'.format(' '.join(map(str, literal)))

    if len(literal_lst) == 1: return literal_to_pddl(literal_lst[0])
    return '(and {})'.format(' '.join(map(str, [literal_to_pddl(e) for e in literal_lst])))


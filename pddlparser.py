# This file is part of pypddl-parser.

# pypddl-parser is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# pypddl-parser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with pypddl-parser.  If not, see <http://www.gnu.org/licenses/>.

from ply import lex, yacc
from fractions import Fraction
import re, io

import domain
import problem

tokens = (
    'NAME',
    'VARIABLE',
    'PROBABILITY',
    'LPAREN',
    'RPAREN',
    'HYPHEN',
    'EQUALS',
    'DEFINE_KEY',
    'DOMAIN_KEY',
    'REQUIREMENTS_KEY',
    'ADL_KEY',
    'STRIPS_KEY',
    'EQUALITY_KEY',
    'TYPING_KEY',
    'PROBABILISTIC_EFFECTS_KEY',
    'NON_DETERMINISTIC_KEY',
    'CONDITIONAL_EFFECTS_KEY',
    'EXISTENTIAL_PRECONDITIONS_KEY',
    'NEGATIVE_PRECONDITIONS_KEY',
    'UNIVERSAL_PRECONDITIONS_KEY',
    'DISJUNCTIVE_PRECONDITIONS_KEY',
    'TYPES_KEY',
    'PREDICATES_KEY',
    'ACTION_KEY',
    'PARAMETERS_KEY',
    'PRECONDITION_KEY',
    'EFFECT_KEY',
    'AND_KEY',
    'NOT_KEY',
    'PROBABILISTIC_KEY',
    'PROBLEM_KEY',
    'ONEOF_KEY',
    'OBJECTS_KEY',
    'CONSTANTS_KEY',
    'INIT_KEY',
    'GOAL_KEY',
    'WHEN_KEY',
    'EXISTS_KEY',
    'FORALL_KEY'
)


t_LPAREN = r'\('
t_RPAREN = r'\)'
t_HYPHEN = r'\-'
t_EQUALS = r'='

t_ignore = ' \t'

reserved = {
    'define'                    : 'DEFINE_KEY',
    'domain'                    : 'DOMAIN_KEY',
    ':requirements'             : 'REQUIREMENTS_KEY',
    ':adl'                      : 'ADL_KEY',
    ':strips'                   : 'STRIPS_KEY',
    ':equality'                 : 'EQUALITY_KEY',
    ':typing'                   : 'TYPING_KEY',
    ':existential-preconditions': 'EXISTENTIAL_PRECONDITIONS_KEY',
    ':negative-preconditions'   : 'NEGATIVE_PRECONDITIONS_KEY',
    ':universal-preconditions'  : 'UNIVERSAL_PRECONDITIONS_KEY',
    ':conditional-effects'      : 'CONDITIONAL_EFFECTS_KEY',
    ':probabilistic-effects'    : 'PROBABILISTIC_EFFECTS_KEY',
    ':non-deterministic'        : 'NON_DETERMINISTIC_KEY',
    ':disjunctive-preconditions': 'DISJUNCTIVE_PRECONDITIONS_KEY', 
    ':types'                    : 'TYPES_KEY',
    ':predicates'               : 'PREDICATES_KEY',
    ':action'                   : 'ACTION_KEY',
    ':parameters'               : 'PARAMETERS_KEY',
    ':precondition'             : 'PRECONDITION_KEY',
    ':effect'                   : 'EFFECT_KEY',
    'and'                       : 'AND_KEY',
    'not'                       : 'NOT_KEY',
    'probabilistic'             : 'PROBABILISTIC_KEY',
    'oneof'                     : 'ONEOF_KEY',
    'problem'                   : 'PROBLEM_KEY',
    ':domain'                   : 'DOMAIN_KEY',
    ':objects'                  : 'OBJECTS_KEY',
    ':constants'                : 'CONSTANTS_KEY',
    ':init'                     : 'INIT_KEY',
    ':goal'                     : 'GOAL_KEY',
    'when'                      : 'WHEN_KEY',
    'exists'                    : 'EXISTS_KEY',
    'forall'                    : 'FORALL_KEY'
}


def t_KEYWORD(t):
    r':?[a-zA-z_][a-zA-Z_0-9\-]*'
    t.type = reserved.get(t.value, 'NAME')
    return t


def t_NAME(t):
    r'[a-zA-z_][a-zA-Z_0-9\-]*'
    return t


def t_VARIABLE(t):
    r'\?[a-zA-z_][a-zA-Z_0-9\-]*'
    return t


def t_PROBABILITY(t):
    r'[0-9]+/0*[1-9][0-9]*|\d+\.\d+|\.\d+|\d+'
    if is_fraction(t.value):
        t.value = round(float(sum(Fraction(s) for s in t.value.split())), 2)
    else:
        t.value = float(t.value)
    return t


def is_fraction(string):
    '''Return True if the string is a valid fraction'''
    return bool(re.search(r'^-?[0-9]+/0*[1-9][0-9]*$', string))


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    print("Error: illegal character '{}' in line '{}'".format(t.value[0], t.lexer.lineno-1))
    t.lexer.skip(1)


# build the lexer
lex.lex()


def p_pddl(p):
    '''pddl : domain
            | problem
            | domain problem'''
    if len(p) == 2:
      p[0] = p[1]
    elif len(p) == 3:
      p[0] = (p[1], p[2])


def p_domain(p):
    '''domain : LPAREN DEFINE_KEY domain_structure_def_lst RPAREN'''
    name = str()
    requirements, predicates, actions = (), (), ()
    types, constants = {}, {}
    for d in p[3]:
      if 'DOMAIN_KEY' in d:
        name = d[1]
      elif 'REQUIREMENTS_KEY' in d:
        requirements = d[1]
      elif 'TYPES_KEY' in d:
        types = d[1]
      elif 'CONSTANTS_KEY' in d:
        constants = d[1]
      elif 'PREDICATES_KEY' in d:
        predicates = d[1]
      else:
        actions = d

    p[0] = domain.Domain(name, requirements, types, constants, predicates, actions)


def p_domain_structure_def_lst(p):
    '''domain_structure_def_lst : domain_structure_def domain_structure_def_lst
                         | domain_structure_def'''
    if len(p) == 2:
        p[0] = tuple([p[1]])
    elif len(p) == 3:
        p[0] = tuple([p[1]]) + p[2]


def p_domain_structure_def(p):
    '''domain_structure_def : domain_def
                     | require_def 
                     | types_def 
                     | constants_def 
                     | predicates_def
                     | action_def_lst'''
    p[0] = p[1]


def p_domain_def(p):
    '''domain_def : LPAREN DOMAIN_KEY NAME RPAREN'''
    p[0] = (['DOMAIN_KEY', p[3]])


def p_require_def(p):
    '''require_def : LPAREN REQUIREMENTS_KEY require_key_lst RPAREN'''
    p[0] = (['REQUIREMENTS_KEY', p[3]])


def p_require_key_lst(p):
    '''require_key_lst : require_key require_key_lst
                       | require_key'''
    if len(p) == 2:
        p[0] = tuple([p[1]])
    elif len(p) == 3:
        p[0] = tuple([p[1]]) + p[2]


def p_require_key(p):
    '''require_key : ADL_KEY
                   | STRIPS_KEY
                   | EQUALITY_KEY
                   | TYPING_KEY
                   | PROBABILISTIC_EFFECTS_KEY
                   | NON_DETERMINISTIC_KEY
                   | CONDITIONAL_EFFECTS_KEY
                   | EXISTENTIAL_PRECONDITIONS_KEY
                   | NEGATIVE_PRECONDITIONS_KEY
                   | UNIVERSAL_PRECONDITIONS_KEY
                   | DISJUNCTIVE_PRECONDITIONS_KEY'''
    p[0] = str(p[1])


def p_types_def(p):
    '''types_def : LPAREN TYPES_KEY typed_names_lst RPAREN'''
    # '''types_def : LPAREN TYPES_KEY names_lst RPAREN'''
    d = dict() 
    for t, v in list(zip(p[3][::2], p[3][1::2])): 
        d.setdefault(t, []).extend(v) 
    p[0] = (['TYPES_KEY', d])
    # p[0] = (['TYPES_KEY', dict(zip(p[3][::2], p[3][1::2]))])


def p_constants_def(p):
    '''constants_def : LPAREN CONSTANTS_KEY typed_constants_lst RPAREN'''
    # convert the tuple into a dictionary: odd indices as keys and even indices as values
    d = dict() 
    for t, v in list(zip(p[3][::2], p[3][1::2])): 
        d.setdefault(t, []).extend(v) 
    p[0] = (['CONSTANTS_KEY', d])
    # p[0] = (['CONSTANTS_KEY', dict(zip(p[3][::2], p[3][1::2]))])


def p_predicates_def(p):
    '''predicates_def : LPAREN PREDICATES_KEY predicate_def_lst RPAREN'''
    p[0] = (['PREDICATES_KEY', p[3]])


def p_predicate_def_lst(p):
    '''predicate_def_lst : predicate_def predicate_def_lst
                         | predicate_def'''
    if len(p) == 2:
        p[0] = tuple([p[1]])
    elif len(p) == 3:
        p[0] = tuple([p[1]]) + p[2]


def p_predicate_def(p):
    '''predicate_def : LPAREN NAME typed_variables_lst RPAREN
                     | LPAREN NAME RPAREN'''
    if len(p) == 4:
        p[0] = tuple([p[2]])
        # p[0] = tuple([p[2],''])
    elif len(p) == 5:
        p[0] = tuple([p[2]]) + tuple(p[3])


def p_action_def_lst(p):
    '''action_def_lst : action_def action_def_lst
                      | action_def'''
    if len(p) == 2:
        p[0] = tuple([p[1]])
    elif len(p) == 3:
        p[0] = tuple([p[1]]) + p[2]


def p_action_def(p):
    '''action_def : LPAREN ACTION_KEY NAME action_def_body_list RPAREN'''
    parameters, probabilistic, oneof = (), (), ()
    precondition = domain.Precondition()
    effect = domain.Effect()
    for d in p[4]:
      if 'PARAMETERS_KEY' in d:
        parameters = d[1]
      elif 'PRECONDITION_KEY' in d:
        precondition = d[1]
      elif 'EFFECT_KEY' in d:
        effect = d[1][0]
        probabilistic = d[1][1]
        oneof = d[1][2]

    p[0] = domain.Action(p[3], parameters, precondition, effect, probabilistic, oneof)


def p_action_def_body_list(p):
    '''action_def_body_list : action_def_body action_def_body_list
                            | action_def_body'''
    if len(p) == 2:
        p[0] = tuple([p[1]])
    elif len(p) == 3:
        p[0] = tuple([p[1]]) + p[2]


def p_action_def_body(p):
    '''action_def_body : parameters_def
                       | precond_def
                       | effect_def'''
    p[0] = p[1]


def p_parameters_def(p):
    '''parameters_def : PARAMETERS_KEY LPAREN typed_variables_lst RPAREN
                      | PARAMETERS_KEY LPAREN RPAREN'''
    if len(p) == 4:
        p[0] = ['PARAMETERS_KEY', ()]
    elif len(p) == 5:
        p[0] = ['PARAMETERS_KEY', tuple(p[3])]


def p_precond_def(p):
    '''precond_def : PRECONDITION_KEY LPAREN AND_KEY preconds_lst RPAREN
                   | PRECONDITION_KEY LPAREN RPAREN
                   | PRECONDITION_KEY precond'''
    if len(p) == 6:
      prec = p[4]
    elif len(p) == 4:
      prec = []
    elif len(p) == 3:
      prec = [p[2]]

    (literals, universal, existential) = ([],[],[])
    for d in prec:
      if 'FORALL_KEY' in d:
        universal.append(tuple(d[1:]))
      elif 'EXISTS_KEY' in d:
        existential.append(tuple(d[1:]))
      else:
        literals.append(d)

    p[0] = ['PRECONDITION_KEY', domain.Precondition(tuple(literals), tuple(universal), tuple(existential))]


def p_preconds_lst(p):
    '''preconds_lst : precond preconds_lst
                    | precond'''
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = [p[1]] + p[2]


def p_precond(p):
    '''precond : literal
               | universal_precond
               | existential_precond'''
    p[0] = p[1]


def p_universal_precond(p):
    '''universal_precond :
               | LPAREN FORALL_KEY LPAREN typed_variables_lst RPAREN literal RPAREN
               | LPAREN FORALL_KEY LPAREN typed_variables_lst RPAREN LPAREN AND_KEY literals_lst RPAREN RPAREN'''
    if len(p) == 8:
        p[0] = ('FORALL_KEY', tuple(p[4]), tuple([p[6]]))
    elif len(p) == 11:
        p[0] = ('FORALL_KEY', tuple(p[4]), tuple(p[8]))


def p_existential_precond(p):
    '''existential_precond :
               | LPAREN EXISTS_KEY LPAREN typed_variables_lst RPAREN literal RPAREN
               | LPAREN EXISTS_KEY LPAREN typed_variables_lst RPAREN LPAREN AND_KEY literals_lst RPAREN RPAREN'''
    if len(p) == 8:
        p[0] = ('EXISTS_KEY', tuple(p[4]), tuple([p[6]]))
    elif len(p) == 11:
        p[0] = ('EXISTS_KEY', tuple(p[4]), tuple(p[8]))


def p_effect_def(p):
    '''effect_def : EFFECT_KEY LPAREN AND_KEY effect_lst RPAREN
                  | EFFECT_KEY effect'''
    if len(p) == 6:
      effects = p[4]
    elif len(p) == 3:
      effects = [p[2]]

    (literals, forall, when, probabilistic, oneof) = ([],[],[],[],[])
    for effect in effects:
      if 'FORALL_KEY' in effect:
        forall.append(tuple(effect[1:]))
      elif 'WHEN_KEY' in effect:
        when.append(tuple(effect[1:]))
      elif 'PROBABILITY' in effect:
        prob_lst = list()
        for eff in effect[1]:
          lit_lst, for_lst, whn_lst = ([],[],[])
          for e in eff[1]:
            if 'FORALL_KEY' in e: for_lst.append(tuple(e[1:]))
            elif 'WHEN_KEY' in e: whn_lst.append(tuple(e[1:]))
            else: lit_lst.append(e)
          prob_lst.append((eff[0], domain.Effect(tuple(lit_lst), tuple(for_lst), tuple(whn_lst))))
        probabilistic.append(tuple(prob_lst))
      elif 'ONEOF' in effect:
        nd_lst = list()
        for eff in effect[1]:
          lit_lst, for_lst, whn_lst = ([],[],[])
          for e in eff:
            if 'FORALL_KEY' in e: for_lst.append(tuple(e[1:]))
            elif 'WHEN_KEY' in e: whn_lst.append(tuple(e[1:]))
            elif e: lit_lst.append(e)
          nd_lst.append(domain.Effect(tuple(lit_lst), tuple(for_lst), tuple(whn_lst)))
        oneof.append(tuple(nd_lst))
      else:
        literals.append(effect)

    p[0] = ['EFFECT_KEY', (domain.Effect(tuple(literals), tuple(forall), tuple(when)), tuple(probabilistic), tuple(oneof))]


def p_effect_lst(p):
    '''effect_lst : effect effect_lst
                  | effect'''
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = [p[1]] + p[2]


def p_effect(p):
    '''effect : literal
              | conditional_for_eff
              | conditional_when_eff
              | LPAREN PROBABILISTIC_KEY prob_effect_lst RPAREN
              | LPAREN ONEOF_KEY nd_effect_lst RPAREN
              | LPAREN AND_KEY RPAREN'''
    if len(p) == 2:
      p[0] = p[1]
    elif len(p) == 4:
      p[0] = ()
    elif len(p) == 5 and type(p[3][0][0]) == float:
      p[0] = ('PROBABILITY', tuple(p[3]))
    elif len(p) == 5:
      p[0] = ('ONEOF', tuple(p[3]))


def p_nd_effect_lst(p):
    '''nd_effect_lst : nd_effect nd_effect_lst
                     | nd_effect'''
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = [p[1]] + p[2]


def p_nd_effect(p):
    '''nd_effect : LPAREN AND_KEY effect_lst RPAREN
                 | effect'''
    if len(p) == 2:
      p[0] = tuple([p[1]])
    else:
      p[0] = tuple(p[3])


def p_prob_effect_lst(p):
    '''prob_effect_lst : prob_effect prob_effect_lst
                       | prob_effect'''
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = [p[1]] + p[2]


def p_prob_effect(p):
    '''prob_effect : PROBABILITY LPAREN AND_KEY effect_lst RPAREN
                   | PROBABILITY effect'''
    if len(p) == 3:
      p[0] = (p[1], tuple([p[2]]))
    else:
      p[0] = (p[1], tuple(p[4]))


def p_conditional_for_eff(p):
    '''conditional_for_eff :
               | LPAREN FORALL_KEY LPAREN typed_variables_lst RPAREN conditional_when_eff RPAREN
               | LPAREN FORALL_KEY LPAREN typed_variables_lst RPAREN literal RPAREN
               | LPAREN FORALL_KEY LPAREN typed_variables_lst RPAREN LPAREN AND_KEY literals_lst RPAREN RPAREN'''
    if len(p) == 8:
      if 'WHEN_KEY' in p[6]:
        p[0] = ('FORALL_KEY', tuple(p[4]), tuple(p[6][1]), tuple(p[6][2]))
      else:
        p[0] = ('FORALL_KEY', tuple(p[4]), tuple([p[6]]))
    elif len(p) == 11:
        p[0] = ('FORALL_KEY', tuple(p[4]), tuple(p[8]))


def p_conditional_when_eff(p):
    '''conditional_when_eff :
               | LPAREN WHEN_KEY literal literal RPAREN
               | LPAREN WHEN_KEY LPAREN AND_KEY literals_lst RPAREN literal RPAREN
               | LPAREN WHEN_KEY literal LPAREN AND_KEY literals_lst RPAREN RPAREN
               | LPAREN WHEN_KEY LPAREN AND_KEY literals_lst RPAREN LPAREN AND_KEY literals_lst RPAREN RPAREN
               '''
    if len(p) == 6:
        p[0] = ('WHEN_KEY', tuple([p[3]]), tuple([p[4]]))
    elif len(p) == 9:
      if p[4] == 'and':
        p[0] = ('WHEN_KEY', tuple(p[5]), tuple([p[7]]))
      else:
        p[0] = ('WHEN_KEY', tuple([p[3]]), tuple(p[6]))
    elif len(p) == 12:
        p[0] = ('WHEN_KEY', tuple(p[5]), tuple(p[9]))


def p_literals_lst(p):
    '''literals_lst : literal literals_lst
                    | literal'''
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = [p[1]] + p[2]


def p_literal(p):
    '''literal : LPAREN NOT_KEY predicate RPAREN
               | predicate'''
    if len(p) == 2:
        p[0] = (p[1])
    elif len(p) == 5:
        p[0] = (-1, p[3])


def p_ground_predicates_lst(p):
    '''ground_predicates_lst : ground_predicate ground_predicates_lst
                             | ground_predicate'''
    if len(p) == 2:
        p[0] = tuple([p[1]])
    elif len(p) == 3:
        p[0] = tuple([p[1]]) + p[2]


def p_predicate(p):
    '''predicate : LPAREN NAME arguments_lst RPAREN
                 | LPAREN EQUALS VARIABLE VARIABLE RPAREN
                 | LPAREN EQUALS VARIABLE constant RPAREN
                 | LPAREN EQUALS constant VARIABLE RPAREN
                 | LPAREN NAME RPAREN'''
    if len(p) == 4:
        p[0] = tuple([p[2],''])
    elif len(p) == 5:
        p[0] = tuple([p[2]]) + tuple(p[3])
    elif len(p) == 6:
        p[0] = tuple(['=', p[3], p[4]])


def p_arguments_lst(p):
    '''arguments_lst : constant arguments_lst
                     | VARIABLE arguments_lst
                     | constant
                     | VARIABLE'''
    if len(p) == 2:
        p[0] = tuple([p[1]])
    elif len(p) == 3:
        p[0] = tuple([p[1]]) + p[2]


def p_ground_predicate(p):
    '''ground_predicate : LPAREN NAME constants_lst RPAREN
                        | LPAREN NAME RPAREN'''
    if len(p) == 4:
        p[0] = tuple([p[2],''])
    elif len(p) == 5:
        p[0] = tuple([p[2]]) + p[3]


def p_typed_constants_lst(p):
    '''typed_constants_lst : constants_lst HYPHEN type typed_constants_lst
                           | constants_lst HYPHEN type'''
    if len(p) == 4:
        p[0] = (p[3], p[1])
    elif len(p) == 5:
        p[0] = (p[3], p[1]) + p[4]


def p_typed_variables_lst(p):
    '''typed_variables_lst : variables_lst HYPHEN type typed_variables_lst
                           | variables_lst HYPHEN type'''
    if len(p) == 4:
        p[0] = [ tuple([p[3], name]) for name in p[1] ]
    elif len(p) == 5:
        p[0] = [ tuple([p[3], name]) for name in p[1] ] + p[4]


def p_constants_lst(p):
    '''constants_lst : constant constants_lst
                     | constant'''
    if len(p) == 2:
        p[0] = tuple([p[1]])
    elif len(p) == 3:
        p[0] = tuple([p[1]]) + p[2]


def p_variables_lst(p):
    '''variables_lst : VARIABLE variables_lst
                     | VARIABLE'''
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = [p[1]] + p[2]


def p_typed_names_lst(p):
    '''typed_names_lst : names_lst HYPHEN type typed_names_lst
                       | names_lst HYPHEN type
                       | names_lst'''
    if len(p) == 2:
        p[0] = tuple([t for pair in zip(p[1], [()]*len(p[1])) for t in pair])
    elif len(p) == 4:
        p[0] = (p[3], p[1])
    elif len(p) == 5:
        p[0] = (p[3], p[1]) + p[4]


def p_names_lst(p):
    '''names_lst : NAME names_lst
                 | NAME'''
    if len(p) == 1:
        p[0] = tuple([])
    elif len(p) == 2:
        p[0] = tuple([p[1]])
    elif len(p) == 3:
        p[0] = tuple([p[1]]) + p[2]


def p_problem(p):
    '''problem : LPAREN DEFINE_KEY problem_structure_def_lst RPAREN'''
    prob, dom = None, None
    init, goal = tuple(), tuple()
    objects = dict()
    for d in p[3]:
      if 'PROBLEM_KEY' in d:
        prob = d[1]
      elif 'DOMAIN_KEY' in d:
        dom = d[1]
      elif 'OBJECTS_KEY' in d:
        objects = d[1]
      elif 'INIT_KEY' in d:
        init = d[1]
      elif 'GOAL_KEY' in d:
        goal = d[1]

    # add objects to 'objects' attributes of the State class
    problem.State.objects = objects

    p[0] = problem.Problem(prob, dom, problem.State(init), goal)


def p_problem_structure_def_lst(p):
    '''problem_structure_def_lst : problem_structure_def problem_structure_def_lst
                                 | problem_structure_def'''
    if len(p) == 2:
        p[0] = tuple([p[1]])
    elif len(p) == 3:
        p[0] = tuple([p[1]]) + p[2]


def p_problem_structure_def(p):
    '''problem_structure_def : problem_def
                             | domain_def
                             | objects_def
                             | init_def
                             | goal_def'''
    p[0] = p[1]


def p_problem_def(p):
    '''problem_def : LPAREN PROBLEM_KEY NAME RPAREN'''
    p[0] = ('PROBLEM_KEY', p[3])


def p_objects_def(p):
    '''objects_def : LPAREN OBJECTS_KEY typed_constants_lst RPAREN'''
    # convert the tuple into a dictionary: odd indices as keys and even indices as values
    d = dict() 
    for t, v in list(zip(p[3][::2], p[3][1::2])): 
        d.setdefault(t, []).extend(v) 
    p[0] = ('OBJECTS_KEY', d)
    # p[0] = ('OBJECTS_KEY', dict(zip(p[3][::2], p[3][1::2])))


def p_init_def(p):
    '''init_def : LPAREN INIT_KEY LPAREN AND_KEY ground_predicates_lst RPAREN RPAREN
                | LPAREN INIT_KEY ground_predicates_lst RPAREN'''
    if len(p) == 5:
        p[0] = ('INIT_KEY', p[3])
    elif len(p) == 8:
        p[0] = ('INIT_KEY', p[5])


def p_goal_def(p):
    '''goal_def : LPAREN GOAL_KEY LPAREN AND_KEY ground_predicates_lst RPAREN RPAREN
                | LPAREN GOAL_KEY ground_predicates_lst RPAREN'''
    if len(p) == 5:
        p[0] = ('GOAL_KEY', p[3])
    elif len(p) == 8:
        p[0] = ('GOAL_KEY', p[5])


def p_type(p):
    '''type : NAME'''
    p[0] = p[1]


def p_constant(p):
    '''constant : NAME'''
    p[0] = p[1]


def p_error(p):
    print("Error: syntax error when parsing '{}'".format(p))
    exit()


# build parser
yacc.yacc()


class PDDLParser(object):

    @classmethod
    def parse(cls, filename):
        data = cls.__read_input(filename)
        return yacc.parse(data, tracking=True)

    @classmethod
    def __read_input(cls, filename):
        with io.open(filename, 'r', encoding='utf-8') as file:
            data = ''
            for line in file:
                line = line.rstrip().lower()
                line = cls.__strip_comments(line)
                data += '\n' + line
        return data

    @classmethod
    def __strip_comments(cls, line):
        pos = line.find(';')
        if pos != -1:
            line = line[:pos]
        return line

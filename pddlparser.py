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


from ply import lex
from ply import yacc
import re
from fractions import Fraction
import io

from pypddl import Domain, Problem, Action, neg


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
    'STRIPS_KEY',
    'EQUALITY_KEY',
    'TYPING_KEY',
    'PROBABILISTIC_EFFECTS_KEY',
    'EXISTENTIAL_PRECONDITIONS_KEY',
    'NEGATIVE_PRECONDITIONS_KEY',
    'UNIVERSAL_PRECONDITIONS_KEY',
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
    'OBJECTS_KEY',
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
    ':strips'                   : 'STRIPS_KEY',
    ':equality'                 : 'EQUALITY_KEY',
    ':typing'                   : 'TYPING_KEY',
    ':probabilistic-effects'    : 'PROBABILISTIC_EFFECTS_KEY',
    ':existential-preconditions': 'EXISTENTIAL_PRECONDITIONS_KEY',
    ':negative-preconditions'   : 'NEGATIVE_PRECONDITIONS_KEY',
    ':universal-preconditions'  : 'UNIVERSAL_PRECONDITIONS_KEY',
    ':types'                    : 'TYPES_KEY',
    ':predicates'               : 'PREDICATES_KEY',
    ':action'                   : 'ACTION_KEY',
    ':parameters'               : 'PARAMETERS_KEY',
    ':precondition'             : 'PRECONDITION_KEY',
    ':effect'                   : 'EFFECT_KEY',
    'and'                       : 'AND_KEY',
    'not'                       : 'NOT_KEY',
    'probabilistic'             : 'PROBABILISTIC_KEY',
    'problem'                   : 'PROBLEM_KEY',
    ':domain'                   : 'DOMAIN_KEY',
    ':objects'                  : 'OBJECTS_KEY',
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
    r'[0-9]+/0*[1-9][0-9]*|[0-1]\.\d+'
    if is_fraction(t.value):
        t.value = round(float(sum(Fraction(s) for s in t.value.split())), 2)
    else:
        t.value = float(t.value)
    return t


def is_fraction(string):
    """Return True iff the string represents a valid fraction."""
    return bool(re.search(r'^-?[0-9]+/0*[1-9][0-9]*$', string))


def t_newline(t):
    r'\n+'
    t.lineno += len(t.value)


def t_error(t):
    print("Error: illegal character '{0}'".format(t.value[0]))
    t.lexer.skip(1)


# build the lexer
lex.lex()


def p_pddl(p):
    '''pddl : domain
            | problem'''
    p[0] = p[1]


def p_domain(p):
    '''domain : LPAREN DEFINE_KEY domain_def require_def types_def predicates_def action_def_lst RPAREN
              | LPAREN DEFINE_KEY domain_def require_def predicates_def action_def_lst RPAREN'''
    if len(p) == 9:
        p[0] = Domain(p[3], p[4], p[5], p[6], p[7])
    elif len(p) == 8:
        p[0] = Domain(p[3], p[4], [], p[5], p[6])


def p_problem(p):
    '''problem : LPAREN DEFINE_KEY problem_def domain_def objects_def init_def goal_def RPAREN
               | LPAREN DEFINE_KEY problem_def domain_def init_def goal_def RPAREN'''
    if len(p) == 9:
        p[0] = Problem(p[3], p[4], p[5], p[6], p[7])
    elif len(p) == 8:
        p[0] = Problem(p[3], p[4], {}, p[5], p[6])


def p_domain_def(p):
    '''domain_def : LPAREN DOMAIN_KEY NAME RPAREN'''
    p[0] = p[3]


def p_problem_def(p):
    '''problem_def : LPAREN PROBLEM_KEY NAME RPAREN'''
    p[0] = p[3]


def p_objects_def(p):
    '''objects_def : LPAREN OBJECTS_KEY typed_constants_lst RPAREN'''
    # conver the tuple into a dictionary: odd indices as keys and even indices as values
    p[0] = dict(zip(p[3][::2], p[3][1::2]))


def p_init_def(p):
    '''init_def : LPAREN INIT_KEY LPAREN AND_KEY ground_predicates_lst RPAREN RPAREN
                | LPAREN INIT_KEY ground_predicates_lst RPAREN'''
    if len(p) == 5:
        p[0] = p[3]
    elif len(p) == 8:
        p[0] = p[5]


def p_goal_def(p):
    '''goal_def : LPAREN GOAL_KEY LPAREN AND_KEY ground_predicates_lst RPAREN RPAREN
                | LPAREN GOAL_KEY ground_predicates_lst RPAREN'''
    if len(p) == 5:
        p[0] = p[3]
    elif len(p) == 8:
        p[0] = p[5]


def p_require_def(p):
    '''require_def : LPAREN REQUIREMENTS_KEY require_key_lst RPAREN'''
    p[0] = p[3]


def p_require_key_lst(p):
    '''require_key_lst : require_key require_key_lst
                       | require_key'''
    if len(p) == 2:
        p[0] = tuple([p[1]])
    elif len(p) == 3:
        p[0] = tuple([p[1]]) + p[2]


def p_require_key(p):
    '''require_key : STRIPS_KEY
                   | EQUALITY_KEY
                   | TYPING_KEY
                   | PROBABILISTIC_EFFECTS_KEY
                   | EXISTENTIAL_PRECONDITIONS_KEY
                   | NEGATIVE_PRECONDITIONS_KEY
                   | UNIVERSAL_PRECONDITIONS_KEY'''
    p[0] = str(p[1])


def p_types_def(p):
    '''types_def : LPAREN TYPES_KEY names_lst RPAREN'''
    p[0] = p[3]


def p_predicates_def(p):
    '''predicates_def : LPAREN PREDICATES_KEY predicate_def_lst RPAREN'''
    p[0] = p[3]


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
        p[0] = tuple([p[2],''])
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
    '''action_def : LPAREN ACTION_KEY NAME parameters_def action_def_body RPAREN'''
    p[0] = Action(p[3], p[4], p[5][0], p[5][1])


def p_parameters_def(p):
    '''parameters_def : PARAMETERS_KEY LPAREN typed_variables_lst RPAREN
                      | PARAMETERS_KEY LPAREN RPAREN'''
    if len(p) == 4:
        p[0] = ()
    elif len(p) == 5:
        p[0] = tuple(p[3])


def p_action_def_body(p):
    '''action_def_body : precond_def effects_def'''
    #p[0] = (p[1], p[2])

    ## precondition = (literals_lst, existential_lst, universal_lst)
    l, e, u = list(), list(), list()
    for a in p[1]:
        if 'EXISTS_KEY' in a: e.append(a)
        elif 'FORALL_KEY' in a: u.append(a)
        else: l.append(a)
    #print((tuple(l),tuple(e),tuple(u)))
    #p[0] = ((tuple(l),tuple(e),tuple(u)), p[2])
    p[0] = (tuple(l), p[2])


def p_precond_def(p):
    '''precond_def : PRECONDITION_KEY LPAREN AND_KEY preconds_lst RPAREN
                   | PRECONDITION_KEY precond'''
    if len(p) == 3:
        p[0] = tuple([p[2]])
    elif len(p) == 6:
        p[0] = tuple(p[4])


def p_preconds_lst(p):
    '''preconds_lst : precond preconds_lst
                    | precond'''
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = [p[1]] + p[2]


def p_precond(p):
    '''precond : literal
               | LPAREN EXISTS_KEY LPAREN typed_variables_lst RPAREN literal RPAREN
               | LPAREN EXISTS_KEY LPAREN typed_variables_lst RPAREN LPAREN AND_KEY literals_lst RPAREN RPAREN
               | LPAREN FORALL_KEY LPAREN typed_variables_lst RPAREN literal RPAREN
               | LPAREN FORALL_KEY LPAREN typed_variables_lst RPAREN LPAREN AND_KEY literals_lst RPAREN RPAREN'''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 8:
        #p[0] = tuple()
        if p[2] == 'forall':
            p[0] = ('FORALL_KEY', tuple(p[4]), tuple(p[6]))
        elif p[2] == 'exists':
            p[0] = ('EXISTS_KEY', tuple(p[4]), tuple(p[6]))
    elif len(p) == 11:
        #p[0] = tuple()
        if p[2] == 'forall':
            p[0] = ('FORALL_KEY', tuple(p[4]), tuple(p[8]))
        elif p[2] == 'exists':
            p[0] = ('EXISTS_KEY', tuple(p[4]), tuple(p[8]))


def p_effects_def(p):
    '''effects_def : EFFECT_KEY LPAREN AND_KEY effects_lst RPAREN
                   | EFFECT_KEY effect'''
    if len(p) == 3:
        p[0] = tuple([p[2]])
    elif len(p) == 6:
        p[0] = tuple(p[4])


def p_effects_lst(p):
    '''effects_lst : effect effects_lst
                   | effect'''
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = [p[1]] + p[2]


def p_effect(p):
    '''effect : literal
              | LPAREN PROBABILISTIC_KEY PROBABILITY literal RPAREN
              | LPAREN PROBABILISTIC_KEY PROBABILITY LPAREN AND_KEY literals_lst RPAREN RPAREN'''
    if len(p) == 2:
        p[0] = p[1]
        # p[0] = (1.0, p[1])
    elif len(p) == 6:
        p[0] = (p[3], tuple([p[4]]))
    elif len(p) == 9:
        p[0] = (p[3], tuple(p[6]))


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
        p[0] = neg(p[3])


def p_ground_predicates_lst(p):
    '''ground_predicates_lst : ground_predicate ground_predicates_lst
                             | ground_predicate'''
    if len(p) == 2:
        p[0] = tuple([p[1]])
    elif len(p) == 3:
        p[0] = tuple([p[1]]) + p[2]


def p_predicate(p):
    '''predicate : LPAREN NAME variables_lst RPAREN
                 | LPAREN EQUALS VARIABLE VARIABLE RPAREN
                 | LPAREN NAME RPAREN'''
    if len(p) == 4:
        p[0] = tuple([p[2],''])
    elif len(p) == 5:
        p[0] = tuple([p[2]]) + tuple(p[3])
    elif len(p) == 6:
        p[0] = tuple(['=', p[3], p[4]])


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


def p_names_lst(p):
    '''names_lst : NAME names_lst
                 | NAME'''
    if len(p) == 1:
        p[0] = tuple([])
    elif len(p) == 2:
        p[0] = tuple([p[1]])
    elif len(p) == 3:
        p[0] = tuple([p[1]]) + p[2]


def p_type(p):
    '''type : NAME'''
    p[0] = p[1]


def p_constant(p):
    '''constant : NAME'''
    p[0] = p[1]


def p_error(p):
    print("Error: syntax error when parsing '{}'".format(p))


# build parser
yacc.yacc()


class PDDLParser(object):

    @classmethod
    def parse(cls, filename):
        data = cls.__read_input(filename)
        return yacc.parse(data)

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

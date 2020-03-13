"""
Classes and functions that allow creating a PDDL-like
problem and domain definition for planning
"""
from itertools import product
import os, time

from color import fg_green, fg_red, fg_yellow, fg_blue, fg_voilet, fg_beige, bg_green, bg_red, bg_yellow, bg_blue, bg_voilet

###############################################################################
## DOMAIN CLASS
###############################################################################
class Domain(object):

    def __init__(self, name=None, requirements=(), types={}, constants={}, predicates=(), actions=()):
        """
        Represents a PDDL-like Problem Domain
        @arg name : string name of the given domain
        @arg requirements : tuple of the requirements in the given domain
        @arg types : dictionary of type and subtypes tuples keyed by super-types
        @arg constants : dictionary of constant tuples keyed by type
        @arg predicates : tuple of the predicates in the given domain
        @arg actions : list of Action objects
        """

        self.name = name
        self.requirements = tuple(requirements)
        self.types = dict(types)
        self.predicates = tuple(predicates)
        self.constants = constants
        self.actions = tuple(actions)

    def ground_actions(self, objects):
        """
        Ground all action schemas given a dictionary
        of objects keyed by type
        """
        grounded_actions = list()
        for action in self.actions:
            param_lists = [objects[t] for t in action.types]
            for params in product(*param_lists):
                grounded_actions.append(action.ground(*params))
        return grounded_actions

    def ground(self, action_sig):
        """
        Return the grounded action schema of a given action signature,
        an action signature example: ('move','robot1','room1',',room2')
        """
        for action in self.actions:
            if action.name == action_sig[0]:
                return action.ground(*tuple(action_sig[1:]))
        return None


    def pddl(self, ex_actions=[]):
        """
        create a pddl file of the problem and return its path as a string
        @arg ex_actions : a list of name of actions should be excluded 
        """
        if not os.path.exists("/tmp/pyddl/"):
            os.makedirs("/tmp/pyddl/")
        pddl = "/tmp/pyddl/domain"+str(int(time.time()*1000000))+".pddl"
        with open(pddl, 'w') as f:
            f.write(self.__str__(pddl=True, ex_actions=ex_actions))
            f.close()
        return pddl


    def __str__(self, pddl=False, ex_actions=[]):
        if not pddl:
            domain_str  = '@ Domain: {0}\n'.format(self.name)
            domain_str += '>> requirements: {0}\n'.format(self.requirements)
            if len(self.types) > 0:
                domain_str += '>> types: {0}\n'.format(self.types)
            if len(self.constants) > 0:
                domain_str += '>> constants:\n'
                for type, constants in self.constants.items():
                    domain_str += '   {0} -> {1}\n'.format(type, ', '.join(sorted(constants)))
            domain_str += '>> predicates: \n   {0}\n'.format('\n   '.join(map(str, self.predicates)))
            domain_str += '>> operators:\n   {0}\n'.format(
                '\n   '.join(str(op).replace('\n', '\n   ') for op in self.actions if op.name not in ex_actions))
            return domain_str
        else:
            pddl_str  = '(define (domain {0})\n\n'.format(self.name)
            pddl_str += '  (:requirements {0})\n\n'.format(' '.join(self.requirements))
            if len(self.types) > 0:
                typed_str = '\n          '.join(['{} - {}'.format(' '.join(map(str,v)), k) for k,v in self.types.items() if v])
                untyped_str = ' '.join([k for k,v in self.types.items() if not v])
                pddl_str += '  (:types {} {})\n\n'.format(typed_str,untyped_str)
            if len(self.constants) > 0:
                pddl_str += '  (:constants\n'
                for type in sorted(self.constants.keys())[:-1]:
                    pddl_str += '        {0} - {1}\n'.format(' '.join(sorted(self.constants[type])), type)
                type = sorted(self.constants.keys())[-1]
                pddl_str += '        {0} - {1})\n\n'.format(' '.join(sorted(self.constants[type])), type)
            pddl_str += '  (:predicates'
            for predicate in self.predicates:
                pddl_str += '\n        ({0} {1})'.format(predicate[0],
                    ' '.join(' - '.join(reversed(p)) for p in predicate[1:]))
            pddl_str += ')\n'
            for action in self.actions:
                if action.name not in ex_actions:
                    pddl_str += action.__str__(pddl)
            pddl_str += ')\n'
            return pddl_str


###############################################################################
## PROBLEM CLASS
###############################################################################
class Problem(object):

    def __init__(self, problem=None, domain=None, objects={}, init=(), goal=()):
        """
        Represents a PDDL Problem Specification
        @arg problem : a string specifying the problem name
        @arg domain : a string specifying the domain name
        @arg objects : dictionary of object tuples keyed by type
        @arg init : tuple of initial state predicates
        @arg goal : tuple of goal state predicates
        """

        self.problem = problem
        self.domain = domain
        self.objects = objects
        self.initial_state = State(init, objects)
        self.goals = goal

    def pddl(self, state=None, goals=None):
        """
        create a pddl file of the problem and return its path as a string
        @arg state : a given initial state (default is the problem initial state)
        """
        if not os.path.exists("/tmp/pyddl/"):
            os.makedirs("/tmp/pyddl/")
        pddl = "/tmp/pyddl/prob"+str(int(time.time()*1000000))+".pddl"
        with open(pddl, 'w') as f:
            f.write(self.__str__(pddl=True, state=state, goals=goals))
            f.close()
        return pddl

    def __str__(self, pddl=False, state=None, goals=None):

        if state == None:
            state = self.initial_state

        if goals == None:
            goals = self.goals

        if not pddl:
            problem_str  = '@ Problem: {0}\n'.format(self.problem)
            problem_str += '>> domain: {0}\n'.format(self.domain)
            if len(self.objects) > 0:
                problem_str += '>> objects:\n'
                for type, objects in self.objects.items():
                    problem_str += '   {0} -> {1}\n'.format(type, ', '.join(sorted(objects)))
            problem_str += '>> init:\n   {0}\n'.format('\n   '.join(map(str, self.initial_state.predicates)))
            problem_str += '>> goal:\n   {0}\n'.format('\n   '.join(map(str, goals)))
            return problem_str
        else:
            pddl_str  = '(define (problem {0})\n'.format(self.problem)
            pddl_str += '  (:domain {0})\n'.format(self.domain)
            if len(self.objects) > 0:
                pddl_str += '  (:objects \n'
                for type in sorted(self.objects.keys())[:-1]:
                    pddl_str += '\t\t{0} - {1}\n'.format(' '.join(sorted(self.objects[type])), type)
                type = sorted(self.objects.keys())[-1]
                pddl_str += '\t\t{0} - {1})\n'.format(' '.join(sorted(self.objects[type])), type)
            pddl_str += '  (:init'
            for predicate in state.predicates:
                pddl_str += '\n\t\t({0})'.format(' '.join(map(str, predicate)))
            pddl_str += ')\n'
            pddl_str += '  (:goal (and'
            for predicate in goals:
                pddl_str += '\n\t\t({0})'.format(' '.join(map(str, predicate)))
            pddl_str += ')))\n'
            return pddl_str


###############################################################################
## STATE CLASS
###############################################################################
class State(object):

    def __init__(self, predicates, objects={}):
        """Represents a state"""
        self.predicates = frozenset(predicates)
        self.objects = objects

    def is_true(self, pos_predicates, neg_predicates=()):
        return (all(p in self.predicates for p in pos_predicates) and
                all(p not in self.predicates for p in neg_predicates))

    def apply(self, action):
        """
        Apply the action to this state to produce a new state.
        """
        new_preds = set(self.predicates)
        new_preds |= set(action.add_effects)
        new_preds -= set(action.del_effects)
        for effect in action.when_effects:
            (pos_cnd_lst, neg_cnd_lst, pos_eff_lst, neg_eff_lst) = effect
            if self.is_true(pos_cnd_lst, neg_cnd_lst):
                new_preds |= set(pos_eff_lst)
                new_preds -= set(neg_eff_lst)
        for effect in action.forall_effects:
            (var_lst, pos_eff_lst, neg_eff_lst) = effect
            (types, arg_names) = zip(*var_lst)
            param_lists = [self.objects[t] for t in types]
            for params in product(*param_lists):
                ground = _grounder(arg_names, params)
                new_preds |= set([ground(eff) for eff in pos_eff_lst])
                new_preds -= set([ground(eff) for eff in neg_eff_lst])
    
        return State(new_preds, self.objects)

    def is_empty(self):
        return (len(self.predicates) == 0)

    # Implement __hash__ and __eq__ so we can easily
    # check if we've encountered this state before

    def __hash__(self):
        return hash((self.predicates))

    def __eq__(self, other):
        return (False if other == None else \
                (self.predicates == other.predicates))

    def __str__(self, pddl=False):
        if not pddl:
            return ('%s' % '\n'.join(map(str, self.predicates)))
        else:
            pddl_str = str()
            for predicate in self.predicates:
                pddl_str += '({0}) '.format(' '.join(map(str, predicate)))
            return pddl_str

    def __lt__(self, other):
        return hash(self) < hash(other)

###############################################################################
## PRECONDITION CLASS
###############################################################################
class Precondition(object):

    def __init__(self, literals=(), universal=(), existential=()):
        """
        A precondition schema
        @arg literals : preconditions as a tuple of literals
        @arg universal : tuple of universal-preconditions: [(var_lst),(literals)]
        @arg existential : tuple of existential-preconditions: [(var_lst),(literals)]
        """
        self.literals = literals
        self.universal = universal
        self.existential = existential

    def __str__(self):
        """
        Return the precondition as a string
        """
        precond_str = str()
        if self.literals:
            precond_str += '   literals: {}\n'.format(self.literals)
        for p in self.universal:
            precond_str += '   forall: {} {}\n'.format(p[0],p[1])
        for p in self.existential:
            precond_str += '   exists: {} {}\n'.format(p[0],p[1])
        return precond_str

    def to_pddl(self):
        """
        Return the precondition as a pddl string
        """
        precond_str = '(and'
        for pre in self.literals:
            if pre[0] == -1:
                precond_str += ' (not ({0}))'.format(' '.join(map(str, pre[1:][0])))
            else:
                precond_str += ' ({0})'.format(' '.join(map(str, pre)))
        ## universal-preconditions
        for uni in self.universal:
            types, variables = zip(*uni[0])
            varlist = ' '.join(['%s - %s' % pair for pair in zip(variables, types)])
            precond_str += '\n             (forall ({}) {})'.format(varlist,literals_to_pddl(uni[1]))
        ## existential-preconditions
        for ext in self.existential:
            types, variables = zip(*ext[0])
            varlist = ' '.join(['%s - %s' % pair for pair in zip(variables, types)])
            precond_str += '\n             (exists ({}) {})'.format(varlist,literals_to_pddl(uni[1]))
        precond_str += ')'

        return precond_str

###############################################################################
## EFFECT CLASS
###############################################################################
class Effect(object):

    def __init__(self, literals=(), forall=(), when=()):
        """
        An Effect  schema
        @arg literals : effects as a tuple of literals
        @arg forall : tuple of conditional-effects forall: [(var_lst),(literals)]
        @arg when : tuple of conditional-effects when: [(literals),(literals)]
        """
        self.literals = literals
        self.forall = forall
        self.when = when

    def __str__(self):
        """
        Return the effect as a string
        """
        eff_str = str()
        if self.literals:
            eff_str += '   literals: {}\n'.format(self.literals)
        for p in self.forall:
            eff_str += '   forall: {} {}\n'.format(p[0],p[1])
        for p in self.when:
            eff_str += '   when: {} {}\n'.format(p[0],p[1])
        return eff_str

    def to_pddl(self):
        """
        Return the effect as a pddl string
        """
        (lit_str, for_str, whn_str) = (str(), str(), str())
        for pre in self.literals:
            if pre[0] == -1:
                lit_str += '(not ({0}))'.format(' '.join(map(str, pre[1:][0])))
            else:
                lit_str += '({0})'.format(' '.join(map(str, pre)))
        for uni in self.forall:
            types, variables = zip(*uni[0])
            varlist = ' '.join(['%s - %s' % pair for pair in zip(variables, types)])
            for_str += '(forall ({}) {})'.format(varlist,literals_to_pddl(uni[1]))
        for uni in self.when:
            whn_str += '(when {} {})'.format(literals_to_pddl(uni[0]),literals_to_pddl(uni[1]))

        return (lit_str, for_str, whn_str)


###############################################################################
## ACTION CLASS
###############################################################################
class Action(object):
    """
    An action schema
    """
    def __init__(self, name, parameters=(), preconditions=(), effects=(), \
                 probabilistic=(), oneof=()):
        """
        A PDDL-like action schema
        @arg name : action name for display purposes
        @arg parameters : tuple of ('type', 'param_name') tuples indicating action parameters
        @arg preconditions : a Preconditions object 
        @arg effects : an Effect object
        @arg probabilistic : a tuple of probabilistic effects
        @arg oneof : a tuple of non-deterministic effects
        """
        self.name = name
        if len(parameters) > 0:
            self.types, self.arg_names = zip(*parameters)
        else:
            self.types = tuple()
            self.arg_names = tuple()
        self.preconditions = preconditions
        self.effects = effects
        self.probabilistic = probabilistic
        self.oneof = oneof

    # def ground(self, *args, **kwargs):
    def ground(self, *args):
        return _GroundedAction(self, *args)

    def __str__(self, pddl=False, body=True):
        if not pddl:
            arglist = ', '.join(['%s - %s' % pair for pair in zip(self.arg_names, self.types)])
            operator_str  = '{0}({1})\n'.format(self.name, arglist)
            if body:
                operator_str += '>> precond:\n{}\n'.format(self.preconditions)
                operator_str += '>> effects:\n{}\n'.format(self.effects)
            return operator_str
        else:
            arglist   = ' '.join(['%s - %s' % pair for pair in zip(self.arg_names, self.types)])
            pddl_str  = '\n  (:action {0}\n   :parameters ({1})'.format(self.name, arglist)
            pddl_str += '\n   :precondition\n        {}'.format(self.preconditions.to_pddl())
            pddl_str += '\n   :effect\n        (and {}'.format('\n             '.join(filter(None,self.effects.to_pddl())))
            for probabilistic in self.probabilistic:
                prob_lst = list()
                for prob in probabilistic:
                    prob_str = prob[1].to_pddl()
                    prob_lst.append('{} (and {}{}{})'.format(str(prob[0]), prob_str[0], prob_str[1], prob_str[2]))
                pddl_str += '\n             (probabilistic {})'.format('\n                            '.join(map(str, prob_lst)))
            for oneof in self.oneof:
                oneof_lst = list()
                for one in oneof:
                    oneof_str = one.to_pddl()
                    oneof_lst.append('(and {}{}{})'.format(oneof_str[0], oneof_str[1], oneof_str[2]))
                pddl_str += '\n             (oneof {})'.format('\n                    '.join(map(str, oneof_lst)))
            pddl_str += ')'
            pddl_str += ')\n'
            return pddl_str

def _grounder(arg_names, args):
    """
    Returns a function for grounding predicates and function symbols
    """
    namemap = dict()
    for arg_name, arg in zip(arg_names, args):
        namemap[arg_name] = arg
    def _ground_by_names(predicate):
        return predicate[0:1] + tuple(namemap.get(arg, arg) for arg in predicate[1:])
    return _ground_by_names


###############################################################################
## GROUNDEDACTION CLASS
###############################################################################
class _GroundedAction(object):
    """
    An action schema that has been grounded with objects
    """
    def __init__(self, action, *args):
    # def __init__(self, action, *args, **kwargs):
        self.name = action.name
        ground = _grounder(action.arg_names, args)

        # Ground Action Signature
        # print()
        # print(action.arg_names, args)
        self.sig = ground((self.name,) + action.arg_names)

        # Ground Preconditions
        self.pos_preconditions = list()
        self.neg_preconditions = list()
        ## not yet supported universal precondition
        self.universal_preconditions = list()
        self.existential_preconditions = list()

        ## literals
        for pre in action.preconditions.literals:
            if pre[0] == -1:
                self.neg_preconditions.append(ground(pre[1]))
            else:
                self.pos_preconditions.append(ground(pre))

        # print(fg_yellow('pos_precond:'), self.pos_preconditions)
        # print(fg_yellow('neg_precond:'), self.neg_preconditions)

        ## universal-preconditions
        ## var_list are not grounded here; they are grounded when action is applied in a state
        for precondition in action.preconditions.universal:
            (neg_pre_lst, pos_pre_lst) = ([],[])
            for pre in precondition[1]:
                if pre[0] == -1:
                    neg_pre_lst.append(ground(pre[1]))
                else:
                    pos_pre_lst.append(ground(pre))
            self.universal_preconditions.append((precondition[0], tuple(pos_pre_lst), tuple(neg_pre_lst)))

        # print(fg_yellow('universal_preconditions:'), self.universal_preconditions)

        ## existential-preconditions
        ## var_list are not grounded here; they are grounded when action is applied in a state
        for precondition in action.preconditions.existential:
            (neg_pre_lst, pos_pre_lst) = ([],[])
            for pre in precondition[1]:
                if pre[0] == -1:
                    neg_pre_lst.append(ground(pre[1]))
                else:
                    pos_pre_lst.append(ground(pre))
            self.existential_preconditions.append((precondition[0], tuple(pos_pre_lst), tuple(neg_pre_lst)))

        # print(fg_yellow('existential_preconditions:'), self.existential_preconditions)

        ## Ground Effects
        self.add_effects = list()
        self.del_effects = list()
        self.forall_effects = list()
        self.when_effects = list()
        self.prob_effects = list()

        ## literals
        for effect in action.effects.literals:
            if effect[0] == -1:
                self.del_effects.append(ground(effect[1]))
            else:
                self.add_effects.append(ground(effect))

        ## conditional-effects (forall)
        ## var_list are not grounded here; they are grounded when action is applied in a state
        for effect in action.effects.forall:
            (neg_eff_lst, pos_eff_lst) = ([],[])
            for eff in effect[1]:
                if eff[0] == -1:
                    neg_eff_lst.append(ground(eff[1]))
                else:
                    pos_eff_lst.append(ground(eff))
            self.forall_effects.append((effect[0], tuple(pos_eff_lst), tuple(neg_eff_lst)))

        # print(fg_yellow('forall_effects:'), self.forall_effects)

        ## conditional-effects (when)
        for effect in action.effects.when:
            (pos_cnd_lst, neg_cnd_lst, pos_eff_lst, neg_eff_lst) = ([],[],[],[])
            for eff in effect[0]:
                if eff[0] == -1:
                    neg_cnd_lst.append(ground(eff[1]))
                else:
                    pos_cnd_lst.append(ground(eff))
            for eff in effect[1]:
                if eff[0] == -1:
                    neg_eff_lst.append(ground(eff[1]))
                else:
                    pos_eff_lst.append(ground(eff))
            self.when_effects.append((tuple(pos_cnd_lst), tuple(neg_cnd_lst), tuple(pos_eff_lst), tuple(neg_eff_lst)))

        # print(fg_yellow('when_effects:'), self.when_effects)

        # self.prob_effects = list() # probabilistic effects: a list of list as [[probability, add_effects, del_effects], ...]

        # print(action.oneof)
        # exit()

        # if deterministic:
        #     for effect in action.effects:
        #         if effect[0] == -1:
        #             self.del_effects.append(ground(effect[1]))
        #         elif effect[0] == '+=':
        #             function = ground(effect[1])
        #             value = effect[2]
        #             self.num_effects.append((function, value))
        #         elif effect[0] == '-=':
        #             function = ground(effect[1])
        #             value = -effect[2]
        #             self.num_effects.append((function, value))
        #         else:
        #             self.add_effects.append(ground(effect))
        # # since the planner does not support probabilistic planning
        # # in probabilistic domains, all positive/negative effects 
        # # are ONLY grounded and added into add_effects (del_effects will be empty)
        # # we just make ground probabilistic domains for the final policy representation,
        # # and not for the planning!
        # else:
        #     for effect in action.effects:
        #         # an action is probabilistic if the type of effect[0] is float 
        #         # i.e., effect[0] is the probability, e.g., effect = (0.5, (-1, ('holding', '?x')))
        #         if type(effect[0]) == float:
        #             # probabilistic effects have the form (PROBABILITY tuple_of_effects)
        #             prob_add_eff = list()
        #             prob_del_eff = list()
        #             for eff in effect[1]:
        #                 if eff[0] == -1:
        #                     prob_del_eff.append(ground(eff[1]))
        #                 else:
        #                     prob_add_eff.append(ground(eff))
        #             self.prob_effects.append((effect[0], prob_add_eff, prob_del_eff))
        #             # self.add_effects.append((effect[0], tuple(prob_add_eff)))
        #         elif effect[0] == -1:
        #             # self.add_effects.append((-1, ground(effect[1])))
        #             self.del_effects.append(ground(effect[1]))
        #         else:
        #             self.add_effects.append(ground(effect))


    def sig(self):
        """
        return the action signature in the predicate format, 
        e.g., self.sig = ('move', 'robot1', 'room1', 'room2')
              return: 'move(robot1,room1,room2)'
        """
        return str(self.sig[0]+'('+', '.join(self.sig[1:])+')')

    def __str__(self, body = False):
        if self == None:
            return None 
        # arglist = ', '.join(map(str, self.sig[1:]))
        # operator_str  = '{0}({1})'.format(self.name, arglist)
        operator_str = '({})'.format(' '.join(self.sig))
        if body:
            if self.pos_preconditions:
                operator_str += '>> precond+: {0}\n'.format(', '.join(map(str, self.pos_preconditions)))
            if self.neg_preconditions:
                operator_str += '>> precond-: {0}\n'.format(', '.join(map(str, self.neg_preconditions)))
            if self.add_effects:
                operator_str += '>> effects+: {0}\n'.format(', '.join(map(str, self.add_effects)))
            if self.del_effects:
                operator_str += '>> effects-: {0}\n'.format(', '.join(map(str, self.del_effects)))
            if self.when_effects:
                operator_str += '>> when-: {0}\n'.format(', '.join(map(str, self.when_effects)))
            if self.prob_effects:
                for eff in self.prob_effects:
                    (prob, add_eff, del_eff) = eff
                    operator_str += '>> probability: {0}\n'.format(prob)
                    if add_eff: operator_str += '>> effects+: {0}\n'.format(', '.join(map(str, add_eff)))
                    if del_eff: operator_str += '>> effects-: {0}\n'.format(', '.join(map(str, del_eff)))
                    # operator_str += '>> effects: {0}\n'.format(', '.join(map(str, eff)))
        return operator_str

    def __hash__(self):
        return hash((self.name, self.sig, tuple(self.pos_preconditions), \
            tuple(self.neg_preconditions), tuple(self.add_effects), \
            tuple(self.del_effects), tuple(self.forall_effects), tuple(self.when_effects)))

    def __eq__(self, other):
        return (False if other == None else \
            ((self.name, set(self.sig), set(self.pos_preconditions), set(self.neg_preconditions), \
                set(self.add_effects), set(self.del_effects)) ) == \
            ((other.name, set(other.sig), set(other.pos_preconditions), set(other.neg_preconditions), \
                set(other.add_effects), set(other.del_effects)) ))


## a function to convert a list of literals into a pddl string
def literals_to_pddl(literal_lst):

    def literal_to_pddl(literal):
        if literal[0] == -1:
            return '(not ({0}))'.format(' '.join(map(str, literal[1:][0])))
        return '({0})'.format(' '.join(map(str, literal)))

    if len(literal_lst) == 1: return literal_to_pddl(literal_lst[0])
    return '(and {})'.format(' '.join(map(str, [literal_to_pddl(e) for e in literal_lst])))


def literals_to_predicates(literal_lst):
    '''returns two lists of positive and negative predicates given a list of literals'''
    (neg_predicates, pos_predicates) = ([],[])
    for literal in literal_lst:
        if literal[0] == -1:
            neg_predicates.append(literal[1])
        else:
            pos_predicates.append(literal)
    return (tuple(neg_predicates), tuple(pos_predicates))


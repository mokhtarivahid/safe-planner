"""
Classes and functions that allow creating a PDDL-like
problem and domain definition for planning
"""
from itertools import product
import operator as ops
import re, os, time

NUM_OPS = {
    '>' : ops.gt,
    '<' : ops.lt,
    '=' : ops.eq,
    '>=': ops.ge,
    '<=': ops.le
}

###############################################################################
## DOMAIN CLASS
###############################################################################
class Domain(object):

    def __init__(self, name=None, requirements=(), types=(), constants={}, predicates=(), actions=()):
        """
        Represents a PDDL-like Problem Domain
        @arg name : string name of the given domain
        @arg requirements : tuple of the requirements in the given domain
        @arg types : tuple of the types in the given domain
        @arg constants : dictionary of constant tuples keyed by type
        @arg predicates : tuple of the predicates in the given domain
        @arg actions : list of Action objects
        """

        self.name = name
        self.requirements = tuple(requirements)
        self.types = tuple(types)
        self.predicates = tuple(predicates)
        self.constants = constants
        self.actions = tuple(actions)

    def ground_actions(self, objects):
        """
        Ground all action schemas given a dictionary
        of objects keyed by type
        """
        deterministic = not ':probabilistic-effects' in self.requirements
        grounded_actions = list()
        for action in self.actions:
            param_lists = [objects[t] for t in action.types]
            param_combos = set()
            for params in product(*param_lists):
                param_set = frozenset(params)
                param_combos.add(param_set)
                grounded_actions.append(action.ground(*params, deterministic=deterministic))
        return grounded_actions

    def ground(self, action_sig):
        """
        Return the grounded action schema of a given action signature,
        an action signature example: 'move(robot1,room1,room2)'
        """
        deterministic = not ':probabilistic-effects' in self.requirements
        for action in self.actions:
            if action.name == action_sig[0]:
                return action.ground(*tuple(action_sig[1:]), deterministic=deterministic)
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
                pddl_str += '  (:types {0})\n\n'.format(' '.join(self.types))
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

        # Parse Initial State
        predicates = list()
        functions = dict()
        for predicate in init:
            if predicate[0] == '=':
                functions[predicate[1]] = predicate[2]
            else:
                predicates.append(predicate)
        self.initial_state = State(predicates, functions)

        # Parse Goal State
        self.goals = list()
        self.num_goals = list()
        for g in goal:
            if g[0] in NUM_OPS:
                ng = _num_pred(NUM_OPS[g[0]], *g[1:])
                self.num_goals.append(ng)
            else:
                self.goals.append(g)

    def ground_actions(self, domain):
        """
        Ground actions from domain and returns all grounded action schemas 
        """
        self.grounded_actions = domain.ground_actions(self.objects)
        return self.grounded_actions

    def grounded_actions_of(self, action_name):
        """
        Returns all grounded action schemas of a given action_name 
        """
        return [action for action in self.grounded_actions if action.name == action_name]

    def update_init(self, state):
        """
        Update the initial state of the problem by the given state
        """
        self.initial_state = state

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
            if len(self.initial_state.functions) > 0:
                problem_str += '>> init:\n{0}\n'.format('\n   '.join(map(str, self.initial_state.functions)))
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

    def __init__(self, predicates, functions, cost=0, predecessor=None):
        """Represents a state for A* search"""
        self.predicates = frozenset(predicates)
        self.functions = tuple(functions.items())
        self.f_dict = functions
        self.predecessor = predecessor
        self.cost = cost

    def is_true(self, predicates, num_predicates):
        return (all(p in self.predicates for p in predicates) and
                all(np(self) for np in num_predicates))

    def apply(self, action, monotone=False, prob_eff=0):
        """
        Apply the action to this state to produce a new state.
        If monotone, ignore the delete list (for A* heuristic).
        'prob_eff' is the index of the probabilistic effects to apply. 
        """
        new_preds = set(self.predicates)
        new_preds |= set(action.add_effects)
        if not monotone:
            new_preds -= set(action.del_effects)
        if len(action.prob_effects):
            new_preds |= set(action.prob_effects[prob_eff][1])
            if not monotone:
                new_preds -= set(action.prob_effects[prob_eff][2])
        new_functions = dict()
        new_functions.update(self.functions)
        for function, value in action.num_effects:
            new_functions[function] += value
        return State(new_preds, new_functions, self.cost + 1, (self, action))

    def plan(self):
        """
        Follow backpointers to successor states
        to produce a plan.
        """
        plan = list()
        n = self
        while n.predecessor is not None:
            plan.append(n.predecessor[1])
            n = n.predecessor[0]
        plan.reverse()
        return plan

    def is_empty(self):
        return (len(self.functions) == 0 and len(self.predicates) == 0)

    # Implement __hash__ and __eq__ so we can easily
    # check if we've encountered this state before

    def __hash__(self):
        return hash((self.predicates, self.functions))

    def __eq__(self, other):
        return (False if other == None else \
                ((self.predicates, self.functions) ==
                 (other.predicates, other.functions)))

    def __str__(self, pddl=False):
        if not pddl:
            if len(self.functions) > 0:
                return ('Predicates:\n%s' % '\n'.join(map(str, self.predicates))
                        +'\nFunctions:\n%s' % '\n'.join(map(str, self.functions)))
            else:
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

    def __init__(self, literals=(), universals=(), existentials=()):
        """
        A precondition schema
        @arg literals : preconditions as literals
        @arg universals : tuple of universal-preconditions
        @arg existentials : tuple of existential-preconditions
        """
        self.literals = literals
        self.universals = universals
        self.existentials = existentials

    def __str__(self, pddl=False):
        """
        Return the precondition as a string
        """
        precond_str = str()
        if not pddl:
            if self.literals:
                precond_str += '  >> literals: {}\n'.format(', '.join(map(str, self.literals)))
            for p in self.universals:
                precond_str += '  >> forall: {} {}\n'.format(p[0],p[1])
            for p in self.existentials:
                precond_str += '  >> exists: {} {}\n'.format(p[0],p[1])
        else:
            precond_str += '(and'
            for pre in self.literals:
                if pre[0] == -1:
                    precond_str += ' (not ({0}))'.format(' '.join(map(str, pre[1:][0])))
                else:
                    precond_str += ' ({0})'.format(' '.join(map(str, pre)))
            ## universal-preconditions
            for uni in self.universals:
                types, variables = zip(*uni[0])
                varlist = ' '.join(['%s - %s' % pair for pair in zip(variables, types)])
                uni_str = str()
                for pre in uni[1]:
                    if pre[0] == -1:
                        uni_str += '(not ({0}))'.format(' '.join(map(str, pre[1:][0])))
                    else:
                        uni_str += '({0})'.format(' '.join(map(str, pre)))
                precond_str += '\n             (forall ({}) (and {}))'.format(varlist,uni_str)
            ## existential-preconditions
            for ext in self.existentials:
                types, variables = zip(*ext[0])
                varlist = ' '.join(['%s - %s' % pair for pair in zip(variables, types)])
                ext_str = str()
                for pre in ext[1]:
                    if pre[0] == -1:
                        ext_str += '(not ({0}))'.format(' '.join(map(str, pre[1:][0])))
                    else:
                        ext_str += '({0})'.format(' '.join(map(str, pre)))
                precond_str += '\n             (exists ({}) (and {}))'.format(varlist,ext_str)
            precond_str += ')'

        return precond_str

###############################################################################
## EFFECT CLASS
###############################################################################
class Effect(object):

    def __init__(self, literals=(), forall=(), when=(), probabilistic=(), oneof=()):
        """
        An Effect  schema
        @arg literals : effects as literals
        @arg forall : tuple of conditional-effects forall
        @arg when : tuple of conditional-effects when
        @arg probabilistic : tuple of probabilistic effects
        @arg oneof : tuple of oneof effects
        """
        self.literals = literals
        self.forall = forall
        self.when = when
        self.probabilistic = probabilistic
        self.oneof = oneof

    def __str__(self, pddl=False):
        """
        Return the effect as a string
        """

        ## a function to convert a conditional effect into a string
        def cnd_effects_str(eff):
            eff_str = str()
            for e in eff: eff_str += cnd_effect_str(e)
            return eff_str

        def cnd_effect_str(eff):
            if 'WHEN_KEY' in eff: return "(when %s %s)" % (eff[1], cnd_effects_str(eff[2]))
            elif 'FORALL_KEY' in eff: return "(forall %s %s)" % (eff[1], cnd_effects_str(eff[2]))
            return str(eff)

        ## a function to convert a conditional effect into a pddl string
        def pddl_cnd_effects_str(eff):
            if len(eff) > 1:
                eff_str = '(and '
                for e in eff: eff_str += pddl_cnd_effect_str(e)
                return eff_str + ')'
            return pddl_cnd_effect_str(eff[0])

        def pddl_cnd_effect_str(eff):
            if 'WHEN_KEY' in eff: return "(when %s %s)" % (pddl_cnd_effects_str(eff[1]), pddl_cnd_effects_str(eff[2]))
            elif 'FORALL_KEY' in eff: return "(forall %s %s)" % (pddl_cnd_effects_str(eff[1]), pddl_cnd_effects_str(eff[2]))
            return pddl_pred_str(eff)

        def pddl_pred_str(pred):
            if pred[0] == -1:
                return '(not ({0}))'.format(' '.join(map(str, pred[1:][0])))
            return '({0})'.format(' '.join(map(str, pred)))


        eff_str = str()
        if not pddl:
            if self.literals:
                eff_str += '  >> literals: {}\n'.format(', '.join(map(str, self.literals)))
            for p in self.forall:
                eff_str += '  >> forall: {}{}\n'.format(p[1],cnd_effects_str(p[2]))
            for p in self.when:
                eff_str += '  >> when: {}{}\n'.format(p[1],cnd_effects_str(p[2]))
            for prob in self.probabilistic:
                eff_str += '  >> probabilistic:\n'
                for p in prob[1]:
                    eff_str += '        ({}) {}\n'.format(p[0],cnd_effects_str(p[1]))
            for prob in self.oneof:
                eff_str += '  >> oneof:\n'
                for p in prob[1]:
                    eff_str += '        {}\n'.format(cnd_effects_str(p))
        else:
            eff_str += '(and'
            for pre in self.literals:
                if pre[0] == -1:
                    eff_str += ' (not ({0}))'.format(' '.join(map(str, pre[1:][0])))
                else:
                    eff_str += ' ({0})'.format(' '.join(map(str, pre)))
            for uni in self.forall:
                types, variables = zip(*uni[1])
                varlist = ' '.join(['%s - %s' % pair for pair in zip(variables, types)])
                eff_str += '\n             (forall ({}) {})'.format(varlist,pddl_cnd_effects_str(uni[2]))
            for uni in self.when:
                eff_str += '\n             (when {} {})'.format(pddl_cnd_effects_str(uni[1]),pddl_cnd_effects_str(uni[2]))
            for prob in self.probabilistic:
                eff_str += '\n             (probabilistic '
                for p in prob[1]:
                    eff_str += '\n                     {} {}'.format(p[0],pddl_cnd_effects_str(p[1]))
                eff_str += ')'
            for prob in self.oneof:
                eff_str += '\n             (oneof '
                for p in prob[1]:
                    eff_str += '\n                     {}'.format(pddl_cnd_effects_str(p))
                eff_str += ')'
            eff_str += ')'

        return eff_str


###############################################################################
## ACTION CLASS
###############################################################################
class Action(object):
    """
    An action schema
    """
    def __init__(self, name, parameters=(), preconditions=(), effects=()):
        """
        A PDDL-like action schema
        @arg name : action name for display purposes
        @arg parameters : tuple of ('type', 'param_name') tuples indicating
                          action parameters
        @arg preconditions : tuple of preconditions for the action in the following format:
                             preconditions = (tuple of literals, tuple of universals, tuple of existentials)
        @arg effects : tuple of effects of the action
        """
        self.name = name
        if len(parameters) > 0:
            self.types, self.arg_names = zip(*parameters)
        else:
            self.types = tuple()
            self.arg_names = tuple()
        ## preconditions = (tuple(literals), tuple(universals), tuple(existentials))
        self.preconditions = preconditions
        self.effects = effects

    # def ground(self, *args, deterministic=True):
    #     return _GroundedAction(self, *args, deterministic=deterministic)
    def ground(self, *args, **kwargs):
        deterministic = kwargs.pop('deterministic', True)
        return _GroundedAction(self, *args, deterministic=deterministic)

    def __str__(self, pddl=False, body=True):
        if not pddl:
            arglist = ', '.join(['%s - %s' % pair for pair in zip(self.arg_names, self.types)])
            operator_str  = '{0}({1})\n'.format(self.name, arglist)
            if body:
                operator_str += '>> precond:\n{}\n'.format(self.preconditions.__str__(pddl))
                operator_str += '>> effects:\n{}\n'.format(self.effects.__str__(pddl))
            return operator_str
        else:
            arglist   = ' '.join(['%s - %s' % pair for pair in zip(self.arg_names, self.types)])
            pddl_str  = '\n  (:action {0}\n   :parameters ({1})'.format(self.name, arglist)
            pddl_str += '\n   :precondition\n        {}'.format(self.preconditions.__str__(pddl))
            pddl_str += '\n   :effect\n        {}'.format(self.effects.__str__(pddl))
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

def _num_pred(op, x, y):
    """
    Returns a numerical predicate that is called on a State.
    """
    def predicate(state):
        operands = [0, 0]
        for i, o in enumerate((x, y)):
            if type(o) == int:
                operands[i] = o
            else:
                operands[i] = state.f_dict[o]
        return op(*operands)
    return predicate

###############################################################################
## GROUNDEDACTION CLASS
###############################################################################
class _GroundedAction(object):
    """
    An action schema that has been grounded with objects
    if @deterministic is True, the actions is deterministic and effects 
    are grounded to add_effects and del_effects; otherwise, the actions 
    is probabilistic and effects are grounded to prob_effects as well
    """
    # def __init__(self, action, *args, deterministic=True):
    def __init__(self, action, *args, **kwargs):
        deterministic = kwargs.pop('deterministic', True)
        self.name = action.name
        ground = _grounder(action.arg_names, args)

        # Ground Action Signature
        self.sig = ground((self.name,) + action.arg_names)

        # Ground Preconditions
        self.preconditions = list()
        self.num_preconditions = list()
        for pre in action.preconditions:
            if pre[0] in NUM_OPS:
                operands = [0, 0]
                for i in range(2):
                    if type(pre[i + 1]) == int:
                        operands[i] = pre[i + 1]
                    else:
                        operands[i] = ground(pre[i + 1])
                np = _num_pred(NUM_OPS[pre[0]], *operands)
                self.num_preconditions.append(np)
            else:
                self.preconditions.append(ground(pre))


        # Ground Effects
        self.add_effects = list()
        self.del_effects = list()
        self.prob_effects = list() # probabilistic effects: a list of list as [[probability, add_effects, del_effects], ...]
        self.num_effects = list()

        if deterministic:
            for effect in action.effects:
                if effect[0] == -1:
                    self.del_effects.append(ground(effect[1]))
                elif effect[0] == '+=':
                    function = ground(effect[1])
                    value = effect[2]
                    self.num_effects.append((function, value))
                elif effect[0] == '-=':
                    function = ground(effect[1])
                    value = -effect[2]
                    self.num_effects.append((function, value))
                else:
                    self.add_effects.append(ground(effect))
        # since the planner does not support probabilistic planning
        # in probabilistic domains, all positive/negative effects 
        # are ONLY grounded and added into add_effects (del_effects will be empty)
        # we just make ground probabilistic domains for the final policy representation,
        # and not for the planning!
        else:
            for effect in action.effects:
                # an action is probabilistic if the type of effect[0] is float 
                # i.e., effect[0] is the probability, e.g., effect = (0.5, (-1, ('holding', '?x')))
                if type(effect[0]) == float:
                    # probabilistic effects have the form (PROBABILITY tuple_of_effects)
                    prob_add_eff = list()
                    prob_del_eff = list()
                    for eff in effect[1]:
                        if eff[0] == -1:
                            prob_del_eff.append(ground(eff[1]))
                        else:
                            prob_add_eff.append(ground(eff))
                    self.prob_effects.append((effect[0], prob_add_eff, prob_del_eff))
                    # self.add_effects.append((effect[0], tuple(prob_add_eff)))
                elif effect[0] == -1:
                    # self.add_effects.append((-1, ground(effect[1])))
                    self.del_effects.append(ground(effect[1]))
                else:
                    self.add_effects.append(ground(effect))


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
            operator_str += '\n>> precond: {0}\n'.format(', '.join(map(str, self.preconditions)))
            if self.add_effects:
                operator_str += '>> effects+: {0}\n'.format(', '.join(map(str, self.add_effects)))
            if self.del_effects:
                operator_str += '>> effects-: {0}\n'.format(', '.join(map(str, self.del_effects)))
            if self.prob_effects:
                for eff in self.prob_effects:
                    (prob, add_eff, del_eff) = eff
                    operator_str += '>> probability: {0}\n'.format(prob)
                    if add_eff: operator_str += '>> effects+: {0}\n'.format(', '.join(map(str, add_eff)))
                    if del_eff: operator_str += '>> effects-: {0}\n'.format(', '.join(map(str, del_eff)))
                    # operator_str += '>> effects: {0}\n'.format(', '.join(map(str, eff)))
        return operator_str

    def __hash__(self):
        return hash((self.name, self.sig, tuple(self.preconditions), tuple(self.num_preconditions), \
                     tuple(self.add_effects), tuple(self.del_effects), tuple(self.num_effects)))

    def __eq__(self, other):
        return (False if other == None else \
                ((self.name, set(self.sig), set(self.preconditions), \
                    set(self.num_preconditions), set(self.add_effects), \
                    set(self.del_effects), set(self.num_effects)) ) == \
                ((other.name, set(other.sig), set(other.preconditions), \
                    set(other.num_preconditions), set(other.add_effects), \
                    set(other.del_effects), set(other.num_effects)) ))


def neg(effect):
    """
    Makes the given effect a negative (delete) effect, like 'not' in PDDL.
    """
    return (-1, effect)

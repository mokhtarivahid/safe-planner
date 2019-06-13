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

    def __init__(self, name=None, requirements=(), types=(), predicates=(), actions=()):
        """
        Represents a PDDL-like Problem Domain
        @arg name : string name of the given domain
        @arg requirements : tuple of the requirements in the given domain
        @arg types : tuple of the types in the given domain
        @arg predicates : tuple of the predicates in the given domain
        @arg actions : list of Action objects
        """

        self.name = name
        self.requirements = tuple(requirements)
        self.types = tuple(types)
        self.predicates = tuple(predicates)
        self.actions = tuple(actions)

    def ground_actions(self, objects):
        """
        Ground all action schemas given a dictionary
        of objects keyed by type
        """
        grounded_actions = list()
        for action in self.actions:
            param_lists = [objects[t] for t in action.types]
            param_combos = set()
            for params in product(*param_lists):
                param_set = frozenset(params)
                if action.unique and len(param_set) != len(params):
                    continue
                if action.no_permute and param_set in param_combos:
                    continue
                param_combos.add(param_set)
                grounded_actions.append(action.ground(*params))
        return grounded_actions

    def ground(self, action_sig):
        """
        Return the grounded action schema of a given action signature,
        an action signature example: 'move(robot1,room1,room2)'
        """
        for action in self.actions:
            if action.name == action_sig[0]:
                return action.ground(*tuple(action_sig[1:]))
        return None


    def to_pddl(self, ex_actions=[]):
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
            domain_str += '>> predicates: \n    {0}\n'.format('\n    '.join(map(str, self.predicates)))
            domain_str += '>> operators:\n    {0}\n'.format(
                '\n    '.join(str(op).replace('\n', '\n    ') for op in self.actions if op.name not in ex_actions))
            return domain_str
        else:
            pddl_str  = '(define (domain {0})\n\n'.format(self.name)
            pddl_str += '  (:requirements {0})\n\n'.format(' '.join(self.requirements))
            if len(self.types) > 0:
                pddl_str += '  (:types {0})\n\n'.format(' '.join(self.types))
            pddl_str += '  (:predicates'
            for predicate in self.predicates:
                pddl_str += '\n\t({0} {1})'.format(predicate[0],
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

    def to_pddl(self, state=None):
        """
        create a pddl file of the problem and return its path as a string
        @arg state : a given initial state (default is the problem initial state)
        """
        if not os.path.exists("/tmp/pyddl/"):
            os.makedirs("/tmp/pyddl/")
        pddl = "/tmp/pyddl/prob"+str(int(time.time()*1000000))+".pddl"
        with open(pddl, 'w') as f:
            f.write(self.__str__(pddl=True, state=state))
            f.close()
        return pddl

    def __str__(self, pddl=False, state=None):
        if state == None:
            state = self.initial_state
        if not pddl:
            problem_str  = '@ Problem: {0}\n'.format(self.problem)
            problem_str += '>> domain: {0}\n'.format(self.domain)
            if len(self.objects) > 0:
                problem_str += '>> objects:\n'
                for type, objects in self.objects.items():
                    problem_str += '{0} -> {1}\n'.format(type, ', '.join(sorted(objects)))
            problem_str += '>> init:\n{0}\n'.format('\n'.join(map(str, self.initial_state.predicates)))
            if len(self.initial_state.functions) > 0:
                problem_str += '>> init:\n{0}\n'.format('\n'.join(map(str, self.initial_state.functions)))
            problem_str += '>> goal:\n{0}\n'.format('\n'.join(map(str, self.goals)))
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
            for predicate in self.goals:
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

    def apply(self, action, monotone=False):
        """
        Apply the action to this state to produce a new state.
        If monotone, ignore the delete list (for A* heuristic)
        """
        new_preds = set(self.predicates)
        new_preds |= set([add_effect[1] for add_effect in action.add_effects])
        if not monotone:
            new_preds -= set([del_effect[1] for del_effect in action.del_effects])
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
        if pddl == False:
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
## ACTION CLASS
###############################################################################
class Action(object):
    """
    An action schema
    """
    def __init__(self, name, parameters=(), preconditions=(), effects=(),
                 unique=False, no_permute=False):
        """
        A PDDL-like action schema
        @arg name : action name for display purposes
        @arg parameters : tuple of ('type', 'param_name') tuples indicating
                          action parameters
        @arg preconditions : tuple of preconditions for the action
        @arg effects : tuple of effects of the action
        @arg unique : if True, only ground with unique arguments (no duplicates)
        @arg no_permute : if True, do not ground an action twice with the same
                          set of (permuted) arguments
        """
        self.name = name
        if len(parameters) > 0:
            self.types, self.arg_names = zip(*parameters)
        else:
            self.types = tuple()
            self.arg_names = tuple()
        self.preconditions = preconditions
        self.effects = effects
        self.unique = unique
        self.no_permute = no_permute

    def ground(self, *args):
        return _GroundedAction(self, *args)

    def __str__(self, pddl=False, body=True):
        if not pddl:
            arglist = ', '.join(['%s - %s' % pair for pair in zip(self.arg_names, self.types)])
            operator_str  = '{0}({1})\n'.format(self.name, arglist)
            if body:
                operator_str += '>> precond: {0}\n'.format(', '.join(map(str, self.preconditions)))
                operator_str += '>> effects: {0}\n'.format(', '.join(map(str, self.effects)))
            return operator_str
        else:
            arglist   = ', '.join(['%s - %s' % pair for pair in zip(self.arg_names, self.types)])
            pddl_str  = '\n  (:action {0}\n\t:parameters ({1})\n'.format(self.name, arglist)
            pddl_str += '\t:precondition (and'
            for precondition in self.preconditions:
                if precondition[0] == -1:
                    pddl_str += '\n\t\t\t(not ({0}))'.format(' '.join(map(str, precondition[1:][0])))
                else:
                    pddl_str += '\n\t\t\t({0})'.format(' '.join(map(str, precondition)))
            pddl_str += ')\n'
            pddl_str += '\t:effect (and'
            for effect in self.effects:
                if effect[0] == 1.0:
                    if effect[1][0] == -1:
                        pddl_str += '\n\t\t\t(not ({0}))'.format(' '.join(map(str, effect[1][1])))
                    else:
                        pddl_str += '\n\t\t\t({0})'.format(' '.join(map(str, effect[1])))
                else:
                    if effect[1][0] == -1:
                        pddl_str += '\n\t\t\t(probabilistic {0} (not ({0})))'.format(effect[0], ' '.join(map(str, effect[1][1])))
                    else:
                        pddl_str += '\n\t\t\t(probabilistic {0} ({1}))'.format(effect[0], ' '.join(map(str, effect[1])))

            pddl_str += '))\n'
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
    """
    def __init__(self, action, *args):
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
        self.num_effects = list()
        for effect in action.effects:
            if effect[1][0] == -1:
                self.del_effects.append((effect[0], ground(effect[1][1])))
            elif effect[1][0] == '+=':
                function = ground(effect[1][1])
                value = effect[1][2]
                self.num_effects.append((function, value))
            elif effect[1][0] == '-=':
                function = ground(effect[1][1])
                value = -effect[1][2]
                self.num_effects.append((function, value))
            else:
                self.add_effects.append((effect[0], ground(effect[1])))


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
            operator_str += '>> effects+: {0}\n'.format(', '.join(map(str, self.add_effects)))
            operator_str += '>> effects-: {0}\n'.format(', '.join(map(str, self.del_effects)))
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

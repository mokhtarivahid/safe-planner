"""
Classes and functions for creating a domain object
"""
from itertools import product

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
        Ground all action schemas given a dictionary of objects keyed by type
        """
        grounded_actions = list()
        for action in self.actions:
            param_lists = [objects[t] for t in action.types]
            print(param_lists)
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

    def __str__(self):
        domain_str  = '@ Domain: {0}\n'.format(self.name)
        if len(self.requirements) > 0:
            domain_str += '>> requirements: {0}\n'.format(self.requirements)
        if len(self.types) > 0:
            domain_str += '>> types: {0}\n'.format(self.types)
        if len(self.constants) > 0:
            domain_str += '>> constants:\n'
            for type, constants in self.constants.items():
                domain_str += '   {0} -> {1}\n'.format(type, ', '.join(sorted(constants)))
        domain_str += '>> predicates: \n   {0}\n'.format('\n   '.join(map(str, self.predicates)))
        domain_str += '>> operators:   {0}\n'.format(
            '\n   '.join(str(op).replace('\n', '\n   ') for op in self.actions))
        return domain_str


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
        """Return the precondition as a string"""
        precond_str = str()
        if self.literals:
            precond_str += '\n       -- literals: {}'.format(self.literals)
        for p in self.universal:
            precond_str += '\n       -- forall: {} {}'.format(p[0],p[1])
        for p in self.existential:
            precond_str += '\n       -- exists: {} {}'.format(p[0],p[1])
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
        """Return the effect as a string"""
        eff_str = str()
        if self.literals:
            eff_str += '\n       -- literals: {}'.format(self.literals)
        for p in self.forall:
            eff_str += '\n       -- forall: {} {}'.format(p[0],p[1])
        for p in self.when:
            eff_str += '\n       -- when: {} {}'.format(p[0],p[1])
        return eff_str

    def __bool__(self):
        """Return false if effect is empty, otherwise true"""
        return not (not self.literals and not self.forall and not self.when)

###############################################################################
## ACTION CLASS
###############################################################################
class Action(object):
    """An action schema"""
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

    def __str__(self, body=True):
        arglist = ', '.join(['%s - %s' % pair for pair in zip(self.arg_names, self.types)])
        operator_str  = '\n--------------------------------------------------'
        operator_str += '\n>> action: {0}({1})'.format(self.name, arglist)
        if body:
            operator_str += '\n-- precond:{}'.format(self.preconditions)
            operator_str += '\n-- effects:{}'.format(self.effects)
            for probabilistic in self.probabilistic:
                for prob in probabilistic:
                    operator_str += '\n-- probabilistic:\n       {}{}'.format(str(prob[0]), prob[1])
            for oneof in self.oneof:
                for one in oneof:
                    operator_str += '\n-- oneof:\n{}'.format(one)
        return operator_str

def _grounder(arg_names, args):
    """Returns a function for grounding predicates and function symbols"""
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
    """An action schema that has been grounded with objects"""
    def __init__(self, action, *args):
    # def __init__(self, action, *args, **kwargs):
        self.name = action.name
        ground = _grounder(action.arg_names, args)

        # Ground Action Signature
        self.sig = ground((self.name,) + action.arg_names)

        # Ground Preconditions
        self.pos_preconditions = list()
        self.neg_preconditions = list()
        ## not yet supported universal precondition when applied in a state 
        self.universal_preconditions = list()
        self.existential_preconditions = list()

        ## literals
        for pre in action.preconditions.literals:
            if pre[0] == -1:
                self.neg_preconditions.append(ground(pre[1]))
            else:
                self.pos_preconditions.append(ground(pre))

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

    def sig(self):
        """
        return the action signature in the predicate format, 
        e.g., self.sig = ('move', 'robot1', 'room1', 'room2')
              return: 'move(robot1,room1,room2)'
        """
        return str(self.sig[0]+'('+', '.join(self.sig[1:])+')')

    def __str__(self, body=False):
        if self == None:
            return None 
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


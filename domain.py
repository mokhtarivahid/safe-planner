'''
Classes and functions for creating a domain object
'''
import copy
from itertools import product

###############################################################################
## DOMAIN CLASS
###############################################################################
class Domain(object):

    def __init__(self, name=None, requirements=(), types={}, constants={}, predicates=(), actions=()):
        '''
        Represents a PDDL-like Problem Domain
        @name : string name of the given domain
        @requirements : tuple of the requirements in the given domain
        @types : dictionary of type and subtypes tuples keyed by super-types
        @constants : dictionary of constant tuples keyed by type
        @predicates : tuple of the predicates in the given domain
        @actions : list of Action objects
        '''

        self.name = name
        self.requirements = tuple(requirements)
        self.types = dict(types)
        self.constants = constants
        self.predicates = tuple(predicates)
        self.actions = tuple(actions)

    def ground_all_actions(self, objects):
        '''
        Ground all action schemas given a dictionary of objects keyed by type
        '''
        grounded_actions = list()
        for action in self.actions:
            param_lists = [objects[t] for t in action.types]
            for params in product(*param_lists):
                grounded_actions.append(action.ground(*params))
        return grounded_actions

    def exclusive_ground(self, action_sig):
        '''
        Return the grounded action schema of a given action signature.
        [Ground an action exactly as the given action signature/name.]
        an action signature example: ('move','robot1','room1',',room2')
        '''
        for action in self.actions:
            if action.name == action_sig[0]:
                return action.ground(*tuple(action_sig[1:]))
        return None

    def inclusive_ground(self, action_sig, map_actions={}):
        '''
        Return a grounded action schema of a given action signature: @action_sig.
        @map_actions: is a mapping for the actions names including newly created 
        deterministic actions after compilation.
        [Ground an action from the same parent of the given action signature.]
        an action signature example: ('move','robot1','room1',',room2')
        '''
        for action in self.actions:
            if map_actions[action.name] == map_actions[action_sig[0]]:
                return action.ground(*tuple(action_sig[1:]))
        return None

    def all_inclusive_ground(self, action_sig, map_actions={}):
        '''
        Return a list of grounded action schemas of a given action signature: @action_sig.
        @map_actions: is a mapping for the actions names including newly created 
        deterministic actions after compilation.
        [Ground all actions from the same parent of the given action signature.]
        an action signature example: ('move','robot1','room1',',room2')
        '''
        grounded_actions = []
        for action in self.actions:
            if map_actions[action.name] == map_actions[action_sig[0]]:
                grounded_actions.append(action.ground(*tuple(action_sig[1:])))
        return grounded_actions

    def constrain_domain(self, ex_actions, map_actions={}, nd_actions={}):
        '''
        returns a new domain copied from this domain and makes its actions 
        in the given ex_actions inapplicable in a state 
        @ex_actions : a list of grounded action signatures that should 
        become inapplicable in a state
        '''
        if not ex_actions: return self

        new_domain = copy.deepcopy(self)

        for action in new_domain.actions:
            if map_actions[action.name] in [map_actions[ex_action[0]] for ex_action in ex_actions]:
                # if action is non-deterministic then add also for all other outcomes/names
                if action.name in nd_actions:
                    for i in range(nd_actions[action.name]):
                        new_domain.predicates = tuple(set(new_domain.predicates + \
                            tuple([('disallowed_{}'.format('%s_%s'%(map_actions[action.name],i)),) + \
                            tuple(zip(action.types, action.arg_names))[:5]])))
                        action.preconditions.literals = tuple(set(action.preconditions.literals + \
                            tuple([(-1, (('disallowed_{}'.format('%s_%s'%(map_actions[action.name],i)),) + action.arg_names[:5]))])))
                else:
                    new_domain.predicates = tuple(set(new_domain.predicates + \
                        tuple([('disallowed_{}'.format(action.name),) + \
                        tuple(zip(action.types, action.arg_names))[:5]])))
                    action.preconditions.literals = tuple(set(action.preconditions.literals + \
                        tuple([(-1, (('disallowed_{}'.format(action.name),) + action.arg_names[:5]))])))

        for action in new_domain.actions:
            for ex_action in ex_actions:
                # if ex_action is non-deterministic then add also for all other outcomes/names
                if ex_action[0] in nd_actions:
                    for i in range(nd_actions[ex_action[0]]):
                        action.effects.literals = \
                            tuple(set(action.effects.literals + tuple([(-1, (('disallowed_{}'.format('%s_%s'%(map_actions[ex_action[0]],i)),) + ex_action[1:6]))])))
                else:
                    action.effects.literals = \
                        tuple(set(action.effects.literals + tuple([(-1, (('disallowed_{}'.format(ex_action[0]),) + ex_action[1:6]))])))

        return new_domain

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
        '''
        A precondition schema
        @literals : preconditions as a tuple of literals
        @universal : tuple of universal-preconditions: [(var_lst),(literals)]
        @existential : tuple of existential-preconditions: [(var_lst),(literals)]
        '''
        self.literals = literals
        self.universal = universal
        self.existential = existential

    def __str__(self):
        '''Return the precondition as a string'''
        precond_str = str()
        if self.literals:
            precond_str += '\n       -- literals: {}'.format(self.literals)
        for p in self.universal:
            precond_str += '\n       -- forall: {} {}'.format(p[0],p[1])
        for p in self.existential:
            precond_str += '\n       -- exists: {} {}'.format(p[0],p[1])
        return precond_str

    def __bool__(self):
        '''Return false if effect is empty, otherwise true'''
        return not (not self.literals and not self.universal and not self.existential)

    def __len__(self):
        '''Return length of effects (total length of literals + forall + when)'''
        return len(self.literals) + len(self.universal) + len(self.existential)


###############################################################################
## PRECONDITION CLASS
###############################################################################
class GroundedPrecondition(object):

    def __init__(self, pos_preconditions=(), neg_preconditions=(), universal_preconditions=(), existential_preconditions=()):
        '''
        A precondition schema
        @literals : preconditions as a tuple of literals
        @universal : tuple of universal-preconditions: [(var_lst),(literals)]
        @existential : tuple of existential-preconditions: [(var_lst),(literals)]
        '''
        self.pos_preconditions = pos_preconditions
        self.neg_preconditions = neg_preconditions
        self.universal_preconditions = universal_preconditions
        self.existential_preconditions = existential_preconditions

    def __str__(self):
        '''Return the precondition as a string'''
        precond_str = str()
        if self.pos_preconditions:
            precond_str += '\n       -- pos_preconditions: {}'.format(self.pos_preconditions)
        if self.neg_preconditions:
            precond_str += '\n       -- neg_preconditions: {}'.format(self.neg_preconditions)
        for p in self.universal_preconditions:
            precond_str += '\n       -- forall: {} {}'.format(p[0],p[1])
        for p in self.existential_preconditions:
            precond_str += '\n       -- exists: {} {}'.format(p[0],p[1])
        return precond_str

    def __bool__(self):
        '''Return false if precondition is empty, otherwise true'''
        return not (not self.pos_preconditions and not self.neg_preconditions and not self.universal_preconditions and not self.existential_preconditions)

    def __len__(self):
        '''Return length of precondition (total length of pos_preconditions + neg_preconditions + universal_preconditions + existential_preconditions)'''
        return len(self.pos_preconditions) + len(self.neg_preconditions) + len(self.universal_preconditions) + len(self.existential_preconditions)

    def __hash__(self):
        return hash((tuple(self.pos_preconditions), tuple(self.neg_preconditions),\
                     tuple(self.universal_preconditions), tuple(self.existential_preconditions)))

###############################################################################
## EFFECT CLASS
###############################################################################
class Effect(object):

    def __init__(self, literals=(), forall=(), when=()):
        '''
        An Effect  schema
        @literals : effects as a tuple of literals
        @forall : tuple of conditional-effects forall: [(var_lst),(literals)]
        @when : tuple of conditional-effects when: [(literals),(literals)]
        '''
        self.literals = literals
        self.forall = forall
        self.when = when

    def __str__(self):
        '''Return the effect as a string'''
        eff_str = str()
        if self.literals:
            eff_str += '\n       -- literals: {}'.format(self.literals)
        for p in self.forall:
            if len(p) == 2:
                eff_str += '\n       -- forall: {} {}'.format(p[0],p[1])
            elif len(p) == 3:
                eff_str += '\n       -- forall: {} when: {} {}'.format(p[0],p[1],p[2])
        for p in self.when:
            eff_str += '\n       -- when: {} {}'.format(p[0],p[1])
        return eff_str

    def __bool__(self):
        '''Return false if effect is empty, otherwise true'''
        return not (not self.literals and not self.forall and not self.when)

    def __len__(self):
        '''Return length of effects (total length of literals + forall + when)'''
        return len(self.literals) + len(self.forall) + len(self.when)


###############################################################################
## EFFECT CLASS
###############################################################################
class GroundedEffect(object):

    def __init__(self, add_effects=(), del_effects=(), forall_effects=(), when_effects=()):
        '''
        An Effect  schema
        @literals : effects as a tuple of literals
        @forall : tuple of conditional-effects forall: [(var_lst),(literals)]
        @when : tuple of conditional-effects when: [(literals),(literals)]
        '''
        self.add_effects = add_effects
        self.del_effects = del_effects
        self.forall_effects = forall_effects
        self.when_effects = when_effects

    def __str__(self):
        '''Return the effect as a string'''
        eff_str = str()
        if self.add_effects:
            eff_str += '\n       -- add_effects: {}'.format(self.add_effects)
        if self.del_effects:
            eff_str += '\n       -- del_effects: {}'.format(self.del_effects)
        for p in self.forall_effects:
            if len(p) == 2:
                eff_str += '\n       -- forall: {} {}'.format(p[0],p[1])
            elif len(p) == 3:
                eff_str += '\n       -- forall: {} when: {} {}'.format(p[0],p[1],p[2])
        for p in self.when_effects:
            eff_str += '\n       -- when: {} {}'.format(p[0],p[1])
        return eff_str

    def __bool__(self):
        '''Return false if effect is empty, otherwise true'''
        return not (not self.add_effects and not self.del_effects and not self.forall_effects and not self.when_effects)

    def __len__(self):
        '''Return length of effects (total length of add_effects + del_effects + forall_effects + when_effects)'''
        return len(self.add_effects) + len(self.del_effects) + len(self.forall_effects) + len(self.when_effects)

    def __hash__(self):
        return hash((tuple(self.add_effects), tuple(self.del_effects),\
                     tuple(self.forall_effects), tuple(self.when_effects)))


###############################################################################
## ACTION CLASS
###############################################################################
class Action(object):
    '''An action schema'''
    def __init__(self, name, parameters=(), preconditions=(), effects=(), \
                 probabilistic=(), oneof=()):
        '''
        A PDDL-like action schema
        @name : action name for display purposes
        @parameters : tuple of ('type', 'param_name') tuples indicating action parameters
        @preconditions : a Preconditions object 
        @effects : an Effect object
        @probabilistic : a tuple of probabilistic effects
        @oneof : a tuple of non-deterministic effects
        '''
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
    '''Returns a function for grounding predicates and function symbols'''
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
    '''An action schema that has been grounded with objects'''
    def __init__(self, action, *args):
    # def __init__(self, action, *args, **kwargs):
        self.name = action.name
        ground = _grounder(action.arg_names, args)

        # Ground Action Signature
        self.sig = ground((self.name,) + action.arg_names)

        def _precondition_grounder(precondition):
            '''Action Preconditions Grounder'''
            pos_preconditions, neg_preconditions = [], []
            ## not yet supported universal precondition when applied in a state 
            universal_preconditions, existential_preconditions = [], []

            # if action has precondition
            if action.preconditions:
                ## literals
                for pre in action.preconditions.literals:
                    if pre[0] == -1:
                        neg_preconditions.append(ground(pre[1]))
                    else:
                        pos_preconditions.append(ground(pre))

                ## universal-preconditions
                ## var_list are not grounded here; they are grounded when action is applied in a state
                for precondition in action.preconditions.universal:
                    (neg_pre_lst, pos_pre_lst) = ([],[])
                    for pre in precondition[1]:
                        if pre[0] == -1:
                            neg_pre_lst.append(ground(pre[1]))
                        else:
                            pos_pre_lst.append(ground(pre))
                    universal_preconditions.append((precondition[0], tuple(pos_pre_lst), tuple(neg_pre_lst)))

                ## existential-preconditions
                ## var_list are not grounded here; they are grounded when action is applied in a state
                for precondition in action.preconditions.existential:
                    (neg_pre_lst, pos_pre_lst) = ([],[])
                    for pre in precondition[1]:
                        if pre[0] == -1:
                            neg_pre_lst.append(ground(pre[1]))
                        else:
                            pos_pre_lst.append(ground(pre))
                    existential_preconditions.append((precondition[0], tuple(pos_pre_lst), tuple(neg_pre_lst)))

            return  GroundedPrecondition(pos_preconditions, neg_preconditions, universal_preconditions, existential_preconditions)


        def _effect_grounder(effects):
            '''Action Effects Grounder'''
            add_effects, del_effects, forall_effects, when_effects = [], [], [], []

            # if action has effect
            if effects:
                ## literals
                for effect in effects.literals:
                    if effect[0] == -1:
                        del_effects.append(ground(effect[1]))
                    else:
                        add_effects.append(ground(effect))

                ## conditional-effects (forall)
                ## var_list are not grounded here; they are grounded when action is applied in a state
                for effect in effects.forall:
                    ## (forall (var_lst) (effects))
                    if len(effect) == 2:
                        (neg_eff_lst, pos_eff_lst) = ([],[])
                        for eff in effect[1]:
                            if eff[0] == -1:
                                neg_eff_lst.append(ground(eff[1]))
                            else:
                                pos_eff_lst.append(ground(eff))
                        forall_effects.append((effect[0], tuple(pos_eff_lst), tuple(neg_eff_lst)))
                    ## (forall (var_lst) (when (cnd) (effects)))
                    elif len(effect) == 3:
                        (pos_cnd_lst, neg_cnd_lst, pos_eff_lst, neg_eff_lst) = ([],[],[],[])
                        for eff in effect[1]:
                            if eff[0] == -1:
                                neg_cnd_lst.append(ground(eff[1]))
                            else:
                                pos_cnd_lst.append(ground(eff))
                        for eff in effect[2]:
                            if eff[0] == -1:
                                neg_eff_lst.append(ground(eff[1]))
                            else:
                                pos_eff_lst.append(ground(eff))
                        forall_effects.append((effect[0], tuple(pos_cnd_lst), tuple(neg_cnd_lst), tuple(pos_eff_lst), tuple(neg_eff_lst)))

                ## conditional-effects (when)
                for effect in effects.when:
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
                    when_effects.append((tuple(pos_cnd_lst), tuple(neg_cnd_lst), tuple(pos_eff_lst), tuple(neg_eff_lst)))

            return GroundedEffect(add_effects, del_effects, forall_effects, when_effects)

        # Ground Preconditions
        self.preconditions = _precondition_grounder(action.preconditions)

        ## Ground Effects
        self.effects = _effect_grounder(action.effects)

        ## Ground Probabilistic Effects
        self.prob_effects = []
        for prob_effects in action.probabilistic:
            self.prob_effects.append(tuple([(prob_effect[0], _effect_grounder(prob_effect[1])) for prob_effect in prob_effects]))

        ## Ground Oneof Effects
        self.oneof_effects = []
        for oneof_effects in action.oneof:
            self.oneof_effects.append(tuple([_effect_grounder(oneof_effect) for oneof_effect in oneof_effects]))


    def sig(self):
        '''
        return the action signature in the predicate format, 
        e.g., self.sig = ('move', 'robot1', 'room1', 'room2')
              return: 'move(robot1,room1,room2)'
        '''
        return str(self.sig[0]+'('+', '.join(self.sig[1:])+')')

    def __str__(self, body=False):
        if self == None:
            return None 
        operator_str = '({})'.format(' '.join(self.sig))
        if body:
            if self.preconditions.pos_preconditions:
                operator_str += '\n-- precond+: {0}'.format(', '.join(map(str, self.preconditions.pos_preconditions)))
            if self.preconditions.neg_preconditions:
                operator_str += '\n-- precond-: {0}'.format(', '.join(map(str, self.preconditions.neg_preconditions)))
            if self.effects.add_effects:
                operator_str += '\n-- effects+: {0}'.format(', '.join(map(str, self.effects.add_effects)))
            if self.effects.del_effects:
                operator_str += '\n-- effects-: {0}'.format(', '.join(map(str, self.effects.del_effects)))
            if self.effects.when_effects:
                operator_str += '\n-- when-: {0}'.format(', '.join(map(str, self.effects.when_effects)))
            for prob_effect in self.prob_effects:
                for prob in prob_effect:
                    operator_str += '\n-- probabilistic:\n       {}{}'.format(str(prob[0]), prob[1])
            for oneof_effect in self.oneof_effects:
                for one in oneof_effect:
                    operator_str += '\n-- oneof:\n{}'.format(one)

        return operator_str

    def __hash__(self):
        return hash((self.name, self.sig, self.preconditions, self.effects,\
                     tuple(self.prob_effects), tuple(self.oneof_effects)))

    def __eq__(self, other):
        return (False if other == None else \
            ((self.name, set(self.sig), set(self.preconditions.pos_preconditions), \
                set(self.preconditions.neg_preconditions), set(self.effects.add_effects), \
                set(self.effects.del_effects)) ) == \
            ((other.name, set(other.sig), set(other.preconditions.pos_preconditions), \
                set(other.preconditions.neg_preconditions), set(other.effects.add_effects), \
                set(other.effects.del_effects)) ))

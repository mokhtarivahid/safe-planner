'''
Classes and functions for creating a problem object
'''

from itertools import product

import domain

###############################################################################
## PROBLEM CLASS
###############################################################################
class Problem(object):

    def __init__(self, problem=None, domain=None, init=None, goal=()):
        '''
        Represents a PDDL Problem Specification
        @problem : a string specifying the problem name
        @domain : a string specifying the domain name
        @objects : dictionary of object tuples keyed by type
        @init : a State object as the initial state
        @goal : tuple of goal state predicates
        '''
        self.problem = problem
        self.domain = domain
        self.initial_state = init
        self.goals = goal

    def __str__(self, state=None, goals=None):

        if state == None:
            state = self.initial_state

        if goals == None:
            goals = self.goals

        problem_str  = '@ Problem: {0}\n'.format(self.problem)
        problem_str += '>> domain: {0}\n'.format(self.domain)
        if len(self.initial_state.objects) > 0:
            problem_str += '>> objects: {}\n'.format(self.initial_state.objects)
        problem_str += '>> init:\n   {0}\n'.format('\n   '.join(map(str, state.predicates)))
        problem_str += '>> goal:\n   {0}\n'.format('\n   '.join(map(str, goals)))
        return problem_str


###############################################################################
## STATE CLASS
###############################################################################
class State(object):

    #  dictionary of object tuples keyed by type
    objects = {}

    def __init__(self, predicates):
        '''Represents a state'''
        self.predicates = frozenset(predicates)

    def is_true(self, pos_predicates, neg_predicates=()):
        return (all(p in self.predicates for p in pos_predicates) and
                all(p not in self.predicates for p in neg_predicates))

    def apply(self, action):
        '''
        Apply a deterministic action to this state to produce a new state.
        '''
        new_preds = set(self.predicates)
        new_preds -= set(action.effects.del_effects)
        new_preds |= set(action.effects.add_effects)
        ## apply conditional when effect
        for effect in action.effects.when_effects:
            (pos_cnd_lst, neg_cnd_lst, pos_eff_lst, neg_eff_lst) = effect
            if self.is_true(pos_cnd_lst, neg_cnd_lst):
                new_preds -= set(neg_eff_lst)
                new_preds |= set(pos_eff_lst)
        ## apply conditional forall effect
        for effect in action.effects.forall_effects:
            ## (forall (var_lst) (effects))
            if len(effect) == 3:
                ## first ground var_list in the state
                (var_lst, pos_eff_lst, neg_eff_lst) = effect
                (types, arg_names) = zip(*var_lst)
                param_lists = [self.objects[t] for t in types]
                for params in product(*param_lists):
                    ground = domain._grounder(arg_names, params)
                    new_preds -= set([ground(eff) for eff in neg_eff_lst])
                    new_preds |= set([ground(eff) for eff in pos_eff_lst])
            ## (forall (var_lst) (when (cnd) (effects)))
            elif len(effect) == 5:
                ## first ground var_list in the state
                (var_lst, pos_cnd_lst, neg_cnd_lst, pos_eff_lst, neg_eff_lst) = effect
                (types, arg_names) = zip(*var_lst)
                param_lists = [self.objects[t] for t in types]
                for params in product(*param_lists):
                    ground = domain._grounder(arg_names, params)
                    if self.is_true([ground(eff) for eff in pos_cnd_lst], [ground(eff) for eff in neg_cnd_lst]):
                        new_preds -= set([ground(eff) for eff in neg_eff_lst])
                        new_preds |= set([ground(eff) for eff in pos_eff_lst])
    
        return State(new_preds)

    def apply_nd(self, action):
        '''
        Apply a non-deterministic action to this state to produce a new state.
        '''
        # a list of states after the action application
        states = []

        def application(predicates, effects):
            '''apply @effects in @predicates'''
            new_preds = set(predicates)
            new_preds -= set(effects.del_effects)
            new_preds |= set(effects.add_effects)
            ## apply conditional when effect
            for effect in effects.when_effects:
                (pos_cnd_lst, neg_cnd_lst, pos_eff_lst, neg_eff_lst) = effect
                if self.is_true(pos_cnd_lst, neg_cnd_lst):
                    new_preds -= set(neg_eff_lst)
                    new_preds |= set(pos_eff_lst)
            ## apply conditional forall effect
            for effect in effects.forall_effects:
                ## (forall (var_lst) (effects))
                if len(effect) == 3:
                    ## first ground var_list in the state
                    (var_lst, pos_eff_lst, neg_eff_lst) = effect
                    (types, arg_names) = zip(*var_lst)
                    param_lists = [self.objects[t] for t in types]
                    for params in product(*param_lists):
                        ground = domain._grounder(arg_names, params)
                        new_preds -= set([ground(eff) for eff in neg_eff_lst])
                        new_preds |= set([ground(eff) for eff in pos_eff_lst])
                ## (forall (var_lst) (when (cnd) (effects)))
                elif len(effect) == 5:
                    ## first ground var_list in the state
                    (var_lst, pos_cnd_lst, neg_cnd_lst, pos_eff_lst, neg_eff_lst) = effect
                    (types, arg_names) = zip(*var_lst)
                    param_lists = [self.objects[t] for t in types]
                    for params in product(*param_lists):
                        ground = domain._grounder(arg_names, params)
                        if self.is_true([ground(eff) for eff in pos_cnd_lst], [ground(eff) for eff in neg_cnd_lst]):
                            new_preds -= set([ground(eff) for eff in neg_eff_lst])
                            new_preds |= set([ground(eff) for eff in pos_eff_lst])
            return new_preds

        # deterministic effects
        states.append(State(application(self.predicates, action.effects)))

        # probabilistic effects
        if action.prob_effects:
            ## make all possible combination of probabilistic effects
            prob_effects_lst = list()
            for prob_effects in action.prob_effects:
                if sum([probability[0] for probability in prob_effects]) == 1:
                    prob_effects_lst.append(prob_effects)
                else:
                    prob_effects_lst.append(prob_effects+tuple([(0, domain.GroundedEffect())]))

            for prob_effects in list(product(*prob_effects_lst)):
                if prob_effects:
                    predicates = set(states[0].predicates)
                    for prob_effect in prob_effects:
                        predicates.update(application(predicates, prob_effect[1]))
                    states.append(State( predicates | states[0].predicates ))

        # non-deterministic effects
        if action.oneof_effects:
            ## make all possible combination of oneof effects
            oneof_effects_lst = list()
            for oneof_effects in action.oneof_effects:
                if len(oneof_effects) > 1:
                    oneof_effects_lst.append(oneof_effects)
                else:
                    oneof_effects_lst.append(oneof_effects+tuple([domain.GroundedEffect()]))

            for oneof_effects in list(product(*oneof_effects_lst)):
                if oneof_effects:
                    predicates = set(states[0].predicates)
                    for oneof_effect in oneof_effects:
                        predicates.update(application(predicates, oneof_effect))
                    states.append(State( predicates | states[0].predicates ))

        # non-deterministic action
        if len(states) > 1: return states[1:]

        # deterministic action
        return states

    def constrain_state(self, ex_actions, map_actions={}, nd_actions={}):
        '''
        returns a new state copied from this state and adds 'disallowed' 
        predicates from given @ex_actions into its predicates 
        @ex_actions : a list of grounded action signatures that 
        should become inapplicable in this state
        '''
        if not ex_actions: return self

        # convert self.predicates from frozenset to a list
        predicates = list(self.predicates)

        # add 'disallowed' predicates for given ex_actions
        for ex_action in ex_actions:
            # if ex_action is non-deterministic then add also for all other outcomes/names
            if ex_action[0] in nd_actions:
                for i in range(nd_actions[ex_action[0]]):
                    predicates.append((('disallowed_{}'.format('%s_%s'%(map_actions[ex_action[0]],i)),) + ex_action[1:6]))
            else:
                predicates.append((('disallowed_{}'.format(ex_action[0]),) + ex_action[1:6]))

        # return a new state
        return State(predicates=frozenset(predicates))

    def __bool__(self):
        '''Return false if state is empty, otherwise true'''
        return not (not self.predicates)

    def __len__(self):
        '''Return length of the state (length of predicates)'''
        return len(self.predicates)

    # Implement __hash__ and __eq__ so we can easily
    # check if we've encountered this state before

    def __hash__(self):
        return hash((self.predicates))

    def __eq__(self, other):
        return (False if other == None else \
                (self.predicates == other.predicates))

    def __str__(self):
        return ('%s' % '\n'.join(map(str, self.predicates)))

    def __lt__(self, other):
        return hash(self) < hash(other)

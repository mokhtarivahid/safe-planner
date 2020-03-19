"""
Classes and functions for creating a problem object
"""

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

    def __str__(self, state=None, goals=None):

        if state == None:
            state = self.initial_state

        if goals == None:
            goals = self.goals

        problem_str  = '@ Problem: {0}\n'.format(self.problem)
        problem_str += '>> domain: {0}\n'.format(self.domain)
        if len(self.objects) > 0:
            problem_str += '>> objects: {}\n'.format(self.objects)
        problem_str += '>> init:\n   {0}\n'.format('\n   '.join(map(str, state.predicates)))
        problem_str += '>> goal:\n   {0}\n'.format('\n   '.join(map(str, goals)))
        return problem_str


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

    def __str__(self):
        return ('%s' % '\n'.join(map(str, self.predicates)))

    def __lt__(self, other):
        return hash(self) < hash(other)



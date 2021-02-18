#!/usr/bin/env python

## functions for compiling a non-deterministic domain 
## into a set of deterministic domains

import argparse
import os, time
import json 
from itertools import product
from collections import OrderedDict

import color
import pddl
from domain import Domain, Action, Effect

def parse():
    usage = 'python3 compilation.py <DOMAIN> [-v] [-h]'
    description = "Compiling a non-deterministic domain to a set of deterministic domains."
    parser = argparse.ArgumentParser(usage=usage, description=description)
    parser.add_argument('domain',  type=str, help='path to a PDDL domain file')
    parser.add_argument("-r", "--rank", help="if '-r' not given, the compiled classical planning domains \
        are ranked by the number of effects in Ascending order; and if '-r' given, in Descending order \
        (default=Ascending)", action="store_true", default=False)
    parser.add_argument("-a", "--all", help="by default the planner uses both single-outcome and all-outcome \
        compilation strategies; given '-a' it uses only all-outcome strategy to compile from \
        non-deterministic to classical planning domains (default=False)", action="store_true", default=False)
    parser.add_argument("-v", "--verbose", help="increase output verbosity", 
        action="store_true")

    return parser.parse_args()


# maximum number of allowed single-outcome deterministic domains
MAX_DOMAINS = 4096


###############################################################################
def compilation(domain, rank=False, alloutcome=False, probability=0.4):
    '''given a non-deterministic domain object return 
       a list (set) of deterministic domains'''

    ## NOTE: currently, it is supposed that !!AN ACTION!! does not have both 
    ##       probabilistic and non-deterministic effects simultaneously; 
    ##       but instead it must have either probabilistic or non-deterministic effects.

    ## list of non-deterministic/probabilistic actions: key - name; value - number of possible outcomes
    nd_actions = OrderedDict()

    ## a mapping of actions names: 
    # for non-deterministic actions an extended name is created and 
    # for deterministic actions the mapping is to their original names
    map_actions = dict()

    ## a list of all possible deterministic actions
    deterministic_actions = list()

    for action in domain.actions:

        ## a list of all possible effects separately
        deterministic_effects = list()

        ## split action probabilistic effects into a list of deterministic effects
        ## make all possible combination of probabilistic effects
        probabilistic_effects = list()
        for prob_eff_lst in action.probabilistic:
            # rank by the highest probability
            if rank: prob_eff_lst = tuple(sorted(prob_eff_lst, key=lambda x: x[0], reverse=False))
            if sum([eff[0] for eff in prob_eff_lst]) == 1:
                probabilistic_effects.append(prob_eff_lst)
            elif rank:
                probabilistic_effects.append(\
                    tuple(sorted(tuple([(probability, Effect())])+prob_eff_lst, key=lambda x: x[0], reverse=False)))
            else:
                probabilistic_effects.append(prob_eff_lst+tuple([(0, Effect())]))

        for prob_eff in list(product(*probabilistic_effects)):
            if prob_eff:
                literals_lst, forall_lst, when_lst = [], [], []
                for eff in prob_eff:
                    literals_lst.extend(eff[1].literals)
                    forall_lst.extend(eff[1].forall)
                    when_lst.extend(eff[1].when)
                eff = Effect(action.effects.literals+tuple(literals_lst), \
                        action.effects.forall+tuple(forall_lst), \
                        action.effects.when+tuple(when_lst))
                if eff: deterministic_effects.append(eff)

        ## split action oneof effects into a list of deterministic effects
        ## make all possible combination of oneof effects
        oneof_effects = list()
        if rank:
            for oneof_eff_lst in action.oneof:
                # oneof_effects.append(tuple(sorted(oneof_eff_lst, key=lambda x: x.__len__(), reverse=True)))
                oneof_effects.append(tuple(reversed(oneof_eff_lst)))
        else: oneof_effects = action.oneof

        for oneof_eff in list(product(*oneof_effects)):
            if oneof_eff:
                literals_lst, forall_lst, when_lst = [], [], []
                for eff in oneof_eff:
                    literals_lst.extend(eff.literals)
                    forall_lst.extend(eff.forall)
                    when_lst.extend(eff.when)
                eff = Effect(action.effects.literals+tuple(literals_lst), \
                        action.effects.forall+tuple(forall_lst), \
                        action.effects.when+tuple(when_lst))
                if eff: deterministic_effects.append(eff)

        ## include also the action (deterministic) effects if the total probability is less than 1.0
        ## or if there is only one probabilistic/oneof effect
        if action.effects and ( len(deterministic_effects) == 0 or len(deterministic_effects) == 1): 
            if rank and (action.oneof or \
                         action.probabilistic and action.probabilistic[0][0][0] < probability):
                deterministic_effects.insert(0, action.effects)
            else:
                deterministic_effects.extend([action.effects])

        ## if there is only one probabilistic/oneof effect, then we also need a neutral 
        ## effect, i.e., we add the action preconditions (literals only) as an action effect
        if not action.effects and len(deterministic_effects) == 1:
            # deterministic_effects.extend([Effect()])
            # ideally empty effect should be added, however, some classical planners
            # will fail when an actions has no effect, so, we add the precondition as
            # the action's effect, that is, no effect will apply
            # first, make sure ignoring equalities in preconditions
            precond_lts = tuple(lit for lit in action.preconditions.literals if '=' not in str(lit))
            if rank and action.probabilistic and action.probabilistic[0][0][0] < probability:
                deterministic_effects.insert(0, Effect(literals=precond_lts))
            else:
                deterministic_effects.extend([Effect(literals=precond_lts)])

        ## rank based on the number (length) of effects (EFF)
        ## Descending: reverse=True (rank:False) (default), Ascending: reverse=False (rank=True)
        ## Descending: large to small number of effects
        ## Ascending: small to large number of effects
        deterministic_effects = tuple(sorted(deterministic_effects, key=lambda x: len(x), reverse=not rank))

        ## add current action into map_actions
        map_actions[action.name] = action.name

        ## all possible compiled deterministic actions for current action
        deterministic_action = []

        ## if current action is non-deterministic/probabilistic
        if len(deterministic_effects) > 1:
            ## add action to nd_actions
            nd_actions[action.name] = len(deterministic_effects)
            for i, effect in enumerate(deterministic_effects):
                ## create a new action name for each outcome and add them to mappings
                nd_actions['%s_%s'%(action.name,i)] = len(deterministic_effects)
                map_actions['%s_%s'%(action.name,i)] = action.name
                ## create the action object with the new names
                deterministic_action.append(Action(name='%s_%s'%(action.name,i), \
                        parameters=tuple(zip(action.types, action.arg_names)), \
                        preconditions=action.preconditions, \
                        effects=effect))
        ## if action is already deterministic; then only create an action object for it
        else:
            deterministic_action.append(Action(name=action.name, \
                    parameters=tuple(zip(action.types, action.arg_names)), \
                    preconditions=action.preconditions, \
                    effects=deterministic_effects[0]))
        ## add the compiled actions into deterministic_actions as a tuple
        deterministic_actions.append(tuple(deterministic_action))

    ## test if the length of Cartesian product might exceed the max number (1000)
    if not alloutcome:
        domains_product_len = 1
        for det_actions in deterministic_actions:
             domains_product_len *= len(det_actions)

        # switch to all-outcome
        if domains_product_len > MAX_DOMAINS:
            print(color.fg_yellow('-- the possible combination of single-outcome domains is {}'.format(domains_product_len)))
            print(color.fg_yellow('-- that exceeds the allowed MAX_DOMAINS [{}]'.format(MAX_DOMAINS)))
            print(color.fg_yellow('-- switch to all-outcome compilation\n'))
            alloutcome = True

        # rise a warning to switch to all-outcome
        elif domains_product_len > MAX_DOMAINS/4:
            print(color.fg_green('-- the possible combination of single-outcome domains is {}'.format(domains_product_len)))
            print(color.fg_green('-- this degrades dramatically the planning performance'))
            print(color.fg_green('-- recommended switching to all-outcome by giving the parameter \'-a\'\n'))

    ## make all possible combination of deterministic actions
    if alloutcome:
        # include only all-outcome compilation
        deterministic_actions = [tuple(set().union(*deterministic_actions))]
    else:
        ## include add all-outcome determinization at the end of the list of domains
        deterministic_actions = list(product(*deterministic_actions)) + [tuple(set().union(*deterministic_actions))]

    ## return a list of deterministic domains
    return ([Domain(name = domain.name, \
                requirements = tuple(set(domain.requirements) - set([':probabilistic-effects',':non-deterministic'])), \
                types = domain.types, \
                predicates = domain.predicates, \
                derived_predicates = domain.derived_predicates, \
                constants = domain.constants, \
                actions = tuple(actions)) for actions in deterministic_actions],
            nd_actions,
            map_actions)


###############################################################################
def compile(domain, rank=False, alloutcome=False, verbose=False):
    """
    given the path to a non-deterministic domain, compiles it 
    into a set of deterministic domains and creates pddl files 
    as well as a file containing probabilistic actions names
    """

    if not (':probabilistic-effects' in domain.requirements or\
            ':non-deterministic' in domain.requirements):
        if verbose: 
            print(color.fg_yellow('-- the \':probabilistic-effects\' requirement is not present'))
            print(color.fg_yellow('-- \'{}\' is assumed as a deterministic domain'.format(domain.name)))
        (deterministic_domains, nd_actions, map_actions) = compilation(domain, rank, alloutcome=True)
    else:
        (deterministic_domains, nd_actions, map_actions) = compilation(domain, rank, alloutcome)

    ## create the directory for compiled deterministic domains 
    domains_dir = '/tmp/safe-planner/{}{}/'.format(domain.name, str(int(time.time()*1000000)))
    if not os.path.exists(domains_dir): os.makedirs(domains_dir)

    ## create deterministic domains files
    for i, domain in enumerate(deterministic_domains):
        pddl_file = '%s/%s%03d.pddl' % (domains_dir,domain.name,i+1)
        with open(pddl_file, 'w') as f:
            f.write(pddl.to_pddl(domain))
            f.close()

    ## write nd_actions to a file 
    prob_file = '{}/{}.prob'.format(domains_dir,domain.name)
    with open(prob_file, 'w') as f:
        json.dump(nd_actions, f)
        f.close()

    ## write map_actions to a file 
    map_file = '{}/{}.acts'.format(domains_dir,domain.name)
    with open(map_file, 'w') as f:
        json.dump(map_actions, f)
        f.close()

    if verbose:
        print('{} deterministic domains generated in \'{}\''.format(str(len(deterministic_domains)), domains_dir))

    return domains_dir

###############################################################################
if __name__ == '__main__':

    import pddlparser

    args = parse()

    domain = pddlparser.PDDLParser.parse(args.domain)

    ## if problem is also in the file
    if type(domain) == tuple: domain = domain[0]

    domains_dir = compile(domain, args.rank, args.all)

    if domains_dir is None: 
        print(color.fg_yellow('-- successfully parsed: ') + args.domain)
        exit()

    deterministic_domains = OrderedDict()
    nd_actions = OrderedDict()

    ## parse deterministic pddl domains
    # print([os.path.join(domains_dir, file) for file in os.listdir(domains_dir)])
    for domain in sorted([os.path.join(domains_dir, file) for file in os.listdir(domains_dir)]):
        ## read the probabilistic actions names
        if domain.endswith('.prob'):
            with open(domain) as f:
                nd_actions = json.load(f)
        ## read the deterministic domains
        if domain.endswith('.pddl'):
            deterministic_domains[domain] = pddlparser.PDDLParser.parse(domain)
            print(color.fg_yellow('-- successfully parsed: ') + domain)

    print(color.fg_yellow('-- total number of non-deterministic domains: ') +str(len(deterministic_domains)))
    print(color.fg_yellow('-- non-deterministic actions: ') + str(set(nd_actions.values())))

    if args.verbose:
        for domain_dir, domain in deterministic_domains.items():
            print(color.fg_yellow('-------------------------'))
            print(pddl.to_pddl(domain))

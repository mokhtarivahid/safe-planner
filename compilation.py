#!/usr/bin/env python3

## functions for compiling a non-deterministic domain 
## into a set of deterministic domains

import argparse
from itertools import product
import os, time
from collections import OrderedDict

# from color import fg_green, fg_red, fg_yellow, fg_blue, fg_voilet, fg_beige, bg_voilet, bg_beige
from color import *
from pddlparser import PDDLParser
from pddl import to_pddl
from domain import Domain, Action, Effect

def parse():
    usage = 'python3 compilation.py <DOMAIN> [-v] [-h]'
    description = "Compiling a non-deterministic domain to a set of deterministic domains."
    parser = argparse.ArgumentParser(usage=usage, description=description)
    parser.add_argument('domain',  type=str, help='path to a PDDL domain file')
    parser.add_argument("-v", "--verbose", help="increase output verbosity", 
        action="store_true")

    return parser.parse_args()


###############################################################################
def compilation(domain):
    '''given a non-deterministic domain object return 
       a list (set) of deterministic domains'''

    ## NOTE: currently, it is supposed that an action does not have both  
    ##       probabilistic and non-deterministic effects simultaneously; 
    ##       but it has either probabilistic or non-deterministic effects.

    ## list of non-deterministic/probabilistic actions
    nd_actions = list()

    ## a list of all possible deterministic actions
    deterministic_actions = list()

    for action in domain.actions:

        ## add action to nd_actions if it is non-deterministic/probabilistic
        if len(action.probabilistic) > 0 or len(action.oneof) > 0:
            nd_actions.append(action.name)

        ## a list of all possible effects separately
        deterministic_effects = list()

        ## split action probabilistic effects into a list of deterministic effects
        ## make all possible combination of probabilistic effects
        probabilistic_effects = list()
        for prob_eff_lst in action.probabilistic:
            if sum([eff[0] for eff in prob_eff_lst]) == 1:
                probabilistic_effects.append(prob_eff_lst)
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
        for oneof_eff in list(product(*action.oneof)):
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

        ## include also the action effects if the total probability is less than 1.0
        if action.effects and len(deterministic_effects) == 0: 
            deterministic_effects.extend([action.effects])
        ## if there is only one probabilistic/oneof effect, then we also need a neutral 
        ## effect, i.e., we add the action preconditions (literals only) as an action effect
        if not action.effects and len(deterministic_effects) == 1:
            deterministic_effects.extend([Effect(literals=action.preconditions.literals)])
            # deterministic_effects.extend([Effect()])

        ## add compiled action effects into deterministic_actions
        deterministic_actions.append(\
            tuple([Action(name=action.name, \
                parameters=tuple(zip(action.types, action.arg_names)), \
                preconditions=action.preconditions, \
                effects=effect) for effect in deterministic_effects]))

    ## make all possible combination of deterministic actions
    deterministic_actions = list(product(*deterministic_actions))

    ## return a list of deterministic domains
    return ([Domain(name = domain.name, \
                requirements = tuple(set(domain.requirements)^set([':probabilistic-effects'])), \
                types = domain.types, \
                predicates = domain.predicates, \
                constants = domain.constants, \
                actions = actions) for actions in deterministic_actions],
            nd_actions)


###############################################################################
def compile(domain, verbose=False):
    """
    given the path to a non-deterministic domain, compiles it 
    into a set of deterministic domains and creates pddl files 
    as well as a file containing probabilistic actions names
    """

    if not ':probabilistic-effects' in domain.requirements:
        print('\'{}\' is not non-deterministic'.format(domain.name))
        return ((),())

    (deterministic_domains, nd_actions) = compilation(domain)

    ## create the directory for compiled deterministic domains 
    domains_dir = '/tmp/pyppddl/{}{}/'.format(domain.name, str(int(time.time()*1000000)))
    if not os.path.exists(domains_dir): os.makedirs(domains_dir)

    ## create deterministic domains files
    for i, domain in enumerate(deterministic_domains):
        pddl_file = '%s/%s%03d.pddl' % (domains_dir,domain.name,i+1)
        with open(pddl_file, 'w') as f:
            f.write(to_pddl(domain))
            f.close()

    ## create deterministic domains files
    prob_file = '{}/{}.prob'.format(domains_dir,domain.name)
    with open(prob_file, 'w') as f:
        for action in nd_actions:
            f.write("%s\n" % action)
        f.close()

    if verbose:
        print('{} deterministic domains generated in \'{}\''.format(str(len(deterministic_domains)), domains_dir))

    return domains_dir

###############################################################################
if __name__ == '__main__':

    args = parse()

    domain = PDDLParser.parse(args.domain)

    ## if problem is also in the file
    if type(domain) == tuple: domain = domain[0]

    domains_dir = compile(domain)

    deterministic_domains = OrderedDict()
    nd_actions = list()

    ## parse deterministic pddl domains
    # print([os.path.join(domains_dir, file) for file in os.listdir(domains_dir)])
    for domain in sorted([os.path.join(domains_dir, file) for file in os.listdir(domains_dir)]):
        ## read the probabilistic actions names
        if domain.endswith('.prob'):
            with open(domain) as f:
                nd_actions = f.read().splitlines()
        ## read the deterministic domains
        if domain.endswith('.pddl'):
            deterministic_domains[domain] = PDDLParser.parse(domain)
            print(fg_yellow('-- successfully parsed: ') + domain)

    print(fg_yellow('-- total number of non-deterministic domains: ') +str(len(deterministic_domains)))
    print(fg_yellow('-- non-deterministic actions: ') + str(nd_actions))

    # deterministic_domains, nd_actions = compilation(domain)

    if args.verbose:
        for domain_dir, domain in deterministic_domains.items():
            print(fg_yellow('-------------------------'))
            print(to_pddl(domain))

    # print(fg_yellow('-- total number of non-deterministic domains: ') +str(len(deterministic_domains)))
    # print(fg_yellow('-- non-deterministic actions: ') + str(nd_actions))

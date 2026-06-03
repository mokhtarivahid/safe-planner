#!/usr/bin/env python

import argparse
import os, time

def parse():
    usage = 'python3 main.py <DOMAIN> <PROBLEM> [<PLANNER>] [-v | --verbose N] [-h | --help]'
    description = "Safe-Planner is a non-deterministic planner for PPDDL."
    parser = argparse.ArgumentParser(usage=usage, description=description)

    parser.add_argument('domain',  type=str, help='path to PDDL domain file')
    parser.add_argument('problem', type=str, help='path to PDDL problem file')
    parser.add_argument("planner", type=str, nargs='?', const=1, 
        help="external planner: ff, m, optic, vhpop, ... (default=ff)", default="ff")
    # parser.add_argument("-v", "--verbose", help="increase output verbosity", 
    #     action="store_true")
    parser.add_argument("-v", "--verbose", default=0, type=int, 
        help="increase output verbosity: 0 (nothing), 1 (high-level), 2 (external planners outputs) (default=0)", )

    return parser.parse_args()


###############################################################################
def _atom(atom):
    try:
        return "({})".format(" ".join(str(x) for x in atom))
    except TypeError:
        return str(atom)


def _action_label(action):
    """Render an action either via its `.sig` (preferred) or `__str__`."""
    sig = getattr(action, "sig", None)
    if sig is not None:
        return _atom(sig)
    return str(action)


def gen_dot_plan(plan, del_effect=True, domain_file=None, problem_file=None,
                 prob_actions=None):
    """Render ``plan`` to GraphViz dot.

    Visual style:
      * non-deterministic action steps -> yellow fill (`#fff4c2`)
      * deterministic action steps     -> white fill, plain border
      * dead-end states                -> red fill (`#fadbd8`)
      * goal states                    -> double-circle
    A step is non-deterministic when one of its actions is in ``prob_actions``
    or when it exposes more than one outcome.
    """
    prob_actions = set(prob_actions or ())

    dot_str = []
    dot_str.append('digraph SafePlannerPolicy {')
    dot_str.append('  graph [fontname="helvetica", rankdir=TB, bgcolor="white"];')
    dot_str.append('  node  [fontname="helvetica", fontsize=12, shape=box, '
                   'style="rounded,filled", fillcolor="white", color="#3b4252"];')
    dot_str.append('  edge  [fontname="helvetica", fontsize=10, color="#3b4252"];')

    for level, step in plan.items():
        node = 'n{}'.format(level)

        if step == 'GOAL':
            dot_str.append('  {} [shape=doublecircle, label="GOAL", '
                           'fillcolor="#d5f5e3", color="#1e8449", '
                           'fontcolor="#1e8449"];'.format(node))
            continue

        if step is None:
            dot_str.append('  {} [label="DEAD-END", fillcolor="#fadbd8", '
                           'color="#a93226", fontcolor="#a93226"];'.format(node))
            continue

        (actions, outcomes) = step
        labels = [_action_label(a) for a in actions]
        label = "\\n".join(labels)
        is_nd = (len(outcomes) > 1
                 or any(getattr(a, "sig", (None,))[0] in prob_actions for a in actions))
        if is_nd:
            dot_str.append('  {} [label="{}", fillcolor="#fff4c2", '
                           'color="#caa72c"];'.format(node, label))
        else:
            dot_str.append('  {} [label="{}"];'.format(node, label))

        for (conditions, jump) in outcomes:
            add_list, del_list = ([], [])
            if conditions:
                add_list, del_list = conditions

            parts = []
            if add_list:
                parts.append("+ " + " ".join(_atom(eff) for eff in add_list))
            if del_effect and del_list:
                parts.append("- " + " ".join(_atom(eff) for eff in del_list))
            eff_str = "\\n".join(parts)
            target = 'n{}'.format(jump) if jump != 'GOAL' else 'nGOAL'
            if jump == 'GOAL':
                dot_str.append('  nGOAL [shape=doublecircle, label="GOAL", '
                               'fillcolor="#d5f5e3", color="#1e8449", '
                               'fontcolor="#1e8449"];')
            dot_str.append('  {}->{} [label="{}"];'.format(node, target, eff_str))

    dot_str.append('}')
    dot_text = "\n".join(dot_str)

    if problem_file is not None:
        out = '{}.dot'.format(os.path.splitext(problem_file)[0])
    elif domain_file is not None:
        out = '{}.dot'.format(os.path.splitext(domain_file)[0])
    else:
        os.makedirs("/tmp/safe-planner/", exist_ok=True)
        out = "/tmp/safe-planner/prob{}.dot".format(int(time.time() * 1e6))

    with open(out, 'w') as f:
        f.write(dot_text)
    return out


###############################################################################
if __name__ == '__main__':

    from safe_planner import planner 

    args = parse()

    policy = planner.Planner(args.domain, args.problem, args.planner, args.verbose)

    plan = policy.plan(tree=True)
    policy.print_plan(plan)

    dot_file = gen_dot_plan(plan=plan, del_effect=False, domain_file=args.domain, problem_file=args.problem)
    print(dot_file)

    print('Planning time: %.3f s' % policy.planning_time)
    print('Total number of replannings: %i' % policy.planning_call)
    print('Total number of calls to unsolvable states: %i' % policy.unsolvable_call)

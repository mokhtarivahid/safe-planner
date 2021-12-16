#!/usr/bin/env python

from multiprocessing import Array, Process, Queue
import subprocess, os, sys, re, signal
from collections import OrderedDict

import color

args_profiles = {
    'ff'        : { 0 : '' },
    'ff-x'      : { 0 : '' },
    'm'         : { 1 : '-P 0 -N -m 4096', \
                    0 : '-P 1 -N -m 4096' },
    'probe'     : { 0 : '' },
    'optic-clp' : { 0 : '-c -N',
                    1 : '-m -N',
                    2 : '-E -N' },
    'lpg-td'    : { 0 : '-speed -noout', \
                    1 : '-quality -v off -noout' },
    'lpg'       : { 0 : '-n 1 -noout' },
    'vhpop'     : { 0 : '-g -f DSep-LIFO -s HC -w 5 -l 1500000' },
    'fd'        : { 1 : '--search "astar(lmcut())"', \
                    2 : '--search "astar(add())"',
                    0 : '--evaluator "hff=ff()" --evaluator "hcea=cea()" --search "lazy_greedy([hff, hcea], preferred=[hff, hcea])"'}
}

def kill_pid(pid):
    '''kill a subprocess by pid'''
    # first check if it is still running
    if pid == 0: return 0
    try:
        os.killpg(pid, 0)
    except OSError:
        return 0
    # kill if it is still running
    try:
        os.killpg(pid, signal.SIGTERM)
        # os.killpg(pid, signal.SIGKILL)
    except OSError:
        return 0
    return 0

def kill_jobs(pwd, planners):
    '''kill all subprocess by pid'''
    for planner in planners:
        pid_file = '%s/%s-pid.txt' % (pwd, planner)
        try:
            with open(pid_file, 'r+') as fp:
                pids = fp.readlines() 
                for pid in pids:
                    kill_pid(int(pid.strip()))
                fp.truncate(0)
        except:
            pass

###############################################################################
###############################################################################
def Plan(planners, domain, problem, pwd, verbose=False):
    '''
    calls multiple planners to solve a given problem and as soon as 
    the first planner finds a plan, terminates all other planners and returns 
    '''
    try:
        # if only one planner then no need multiprocessing
        if len(set(planners)) == 1:
            planner = list(planners)[0]
            plan = call_planner_sp(planner, domain, problem, args_profiles[planner][planners[planner]], pwd, verbose)
            if plan == -1:
                if not verbose: 
                    print(color.fg_red('[some error by external planner -- run again with parameter \'-v 2\']'))
                sys.exit(0)
            return plan

        # create a shared Queue to store the output plan
        returned_plan = Queue()

        # a shared Array to store the failed planners
        failed_planners = Array('I', len(planners))

        # store the running processes
        process_lst = []

        # run in multiprocessing
        for pidx, planner in enumerate(planners):
            # proc = Process(target=call_planner_mp, \
            #     args=(planner, domain, problem, args_profiles[planner][planners[planner]], pwd, returned_plan, failed_planners, verbose),
            #     daemon=True)
            proc = Process(target=call_planner_mp, \
                args=(planner, domain, problem, args_profiles[planner][planners[planner]], pwd, returned_plan, failed_planners, verbose))
            proc.daemon = True
            process_lst.append(proc)
            proc.start()

        # wait until one process completes and returns a plan
        while returned_plan.empty():
            # if all processes (planners) failed to solve the problem
            if sum(failed_planners) == len(planners):
                print(color.fg_red('[error by all external planners: run with \'-v 2\']'))
                sys.exit(0)

        # kill running planners (subprocesses) if they are running
        kill_jobs(pwd, planners)

        # make sure processes terminate gracefully
        while process_lst:
            proc = process_lst.pop()
            while proc.is_alive():
                try:
                    proc.terminate()
                    proc.join()
                except: pass

        # return the plan 
        return returned_plan.get()
    # make sure all processes are terminated when KeyboardInterrupt received
    except KeyboardInterrupt:
        if len(planners) > 1:
            kill_jobs(pwd, planners)
            print(color.bg_red('ALL JOBS TERMINATED'))
        raise


###############################################################################
###############################################################################
def call_planner_mp(planner, domain, problem, args, pwd, returned_plan, failed_planners, verbose):
    '''
    Call an external deterministic planner in multi processing.
    Arguments:
    @domain : path to a given domain 
    @problem : path to a given problem 
    @planner : the name of the external planner 
    @args : the default args of the external planner 
    @pwd : the current working directory 
    @returned_plan : is a shared queue and stores the returned plan for every planner
    @failed_planners : is a shared array and stores the failed result for every planner
    @verbose : if True, prints statistics before returning
    '''
    def return_plan(planner, plan=-1):
        if not plan == -1:
            returned_plan.put(plan)
        else:
            try: failed_planners[sum(failed_planners)] = 1
            except: pass
        return

    ## FF planner ##
    if 'ff' in planner.lower():
        plan = call_ff(planner, domain, problem, args, pwd, verbose)
        return_plan(planner, plan)

    ## Madagascar (M) planner ##
    elif 'm' in planner.lower():
        plan = call_m(domain, problem, args, pwd, verbose)
        return_plan(planner, plan)

    ## PROBE planner ##
    elif 'probe' in planner.lower():
        plan = call_probe(domain, problem, args, pwd, verbose)
        return_plan(planner, plan)

    ## optic-clp planner ##
    elif 'optic-clp' in planner.lower() or 'optic' in planner.lower():
        plan = call_optic_clp(domain, problem, args, pwd, verbose)
        return_plan(planner, plan)

    ## optic-clp planner ##
    elif 'vhpop' in planner.lower():
        plan = call_vhpop(domain, problem, args, pwd, verbose)
        return_plan(planner, plan)

    ## lpg-td planner ##
    elif 'lpg-td' in planner.lower():
        plan = call_lpg_td(domain, problem, args, pwd, verbose)
        return_plan(planner, plan)

    ## lpg-td planner ##
    elif 'lpg' in planner.lower():
        plan = call_lpg(domain, problem, args, pwd, verbose)
        return_plan(planner, plan)

    ## lpg-td planner ##
    elif 'fd' in planner.lower():
        plan = call_fd(domain, problem, args, pwd, verbose)
        return_plan(planner, plan)

    ## no planner ##
    else:
        print(color.fg_red("\n[There is not yet a function for parsing the outputs of '{0}'!]\n".format(planner)))
        return_plan(planner)

    return


###############################################################################
###############################################################################
def call_planner_sp(planner, domain, problem, args, pwd, verbose):
    '''
    Call an external deterministic planner in single processing.
    Arguments:
    @domain : path to a given domain 
    @problem : path to a given problem 
    @planner : the name of the external planner  
    @args : the default args of the external planner 
    @pwd : the current working directory 
    @verbose : if True, prints statistics before returning
    '''
    ## FF planner ##
    if 'ff' in planner.lower():
        return call_ff(planner, domain, problem, args, pwd, verbose)

    ## Madagascar (M) planner ##
    elif 'm' in planner.lower():
        return call_m(domain, problem, args, pwd, verbose)

    ## PROBE planner ##
    elif 'probe' in planner.lower():
        return call_probe(domain, problem, args, pwd, verbose)

    ## optic-clp planner ##
    elif 'optic-clp' in planner.lower() or 'optic' in planner.lower():
        return call_optic_clp(domain, problem, args, pwd, verbose)

    ## optic-clp planner ##
    elif 'vhpop' in planner.lower():
        return call_vhpop(domain, problem, args, pwd, verbose)

    ## lpg-td planner ##
    elif 'lpg-td' in planner.lower():
        return call_lpg_td(domain, problem, args, pwd, verbose)

    ## lpg-td planner ##
    elif 'lpg' in planner.lower():
        return call_lpg(domain, problem, args, pwd, verbose)

    ## lpg-td planner ##
    elif 'fd' in planner.lower():
        return call_fd(domain, problem, args, pwd, verbose)

    ## no planner ##
    print(color.fg_red("\n[There is not yet a function for parsing the outputs of '{0}'!]\n".format(planner)))
    # exit()
    return -1


###############################################################################
###############################################################################
## call ff planner
def call_ff(planner, domain, problem, args='', pwd='/tmp', verbose=0):
    '''
    Call an external planner
    @domain : path to a given domain 
    @problem : path to a given problem 
    @args : the default args of the external planner 
    @pwd : the current working directory 
    @verbose : if True, prints statistics before returning

    @return plan : the output plan is a list of actions as tuples, 
                   e.g., [[('move-car', 'l1', 'l4')], [('changetire', 'l4')]]
    '''

    cmd = 'timeout 1800 ./planners/{} -o {} -f {} {}  & echo $! >> {}/ff-pid.txt'.format(planner, domain, problem, args, pwd)

    ## call command ##
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn=os.setsid)

    (output, err) = process.communicate()
    # try:
    #     (output, err) = process.communicate(timeout=1800)
    # except subprocess.TimeoutExpired:
    #     if verbose == 2: print(color.fg_red('\n-- planning timeout (30m)'))
    #     return -1

    ## Wait for cmd to terminate. Get return returncode ##
    if process.wait() < 0: return -1

    ## bytes to string ##
    # shell = ''.join(map(chr, output))
    shell = to_str(output)

    if verbose == 2: 
        print(color.fg_voilet('\n-- planner stdout'))
        print(shell)
        if to_str(err):
            print(color.fg_voilet('-- planner stderr'))
            print(to_str(err))

    # Permission denied
    if 'Permission denied' in to_str(err):
        print(to_str(err))
        print(color.fg_voilet('-- run \'chmod +x planners/ff\''))
        return -1

    ## if no solution exists try the next domain ##
    if "goal can be simplified to FALSE" in shell or "problem proven unsolvable" in shell:
        return None

    ## if solution already exists in the problem ##
    if "goal can be simplified to TRUE" in shell:
        return list()

    ## if solution already exists in the problem ##
    if 'predicate' in shell or 'type mismatch' in shell or\
       'undeclared variable' in shell or 'declared to use unknown' in shell or\
       'unknown constant' in shell or 'check input files' in shell or\
       'increase MAX_PLAN_LENGTH!' in shell or\
       'too many constants!' in shell or 'too many operators!' in shell or\
       'syntax error in line' in to_str(err):
        # print(color.fg_yellow('[planning failed due to some error in the pddl description]'))
        # print(color.fg_voilet('\n-- planner stdout'))
        # print(shell)
        # if to_str(err):
        #     print(color.fg_voilet('-- planner stderr'))
        #     print(to_str(err))
        # exit()
        return -1

    ## refine the output screen and build a plan of actions' signatures ##
    shell = shell[shell.find('step')+len('step'):shell.rfind('time spent')].strip()  # extract plan

    return [[tuple(l.lower().split()[1:])] for l in shell.splitlines()]  # string to list of tuples

###############################################################################
###############################################################################
## call optic-clp planner
def call_optic_clp(domain, problem, args='-b -N', pwd='/tmp', verbose=0):
    '''
    Call an external planner
    @domain : path to a given domain 
    @problem : path to a given problem 
    @verbose : if True, prints statistics before returning

    @return plan : the output plan is a list of actions as tuples, 
                   e.g., [[('move_to_grasp', 'arm1', 'box1', 'base1', 'box2'), ('move_to_grasp', 'arm2', 'box2', 'cap1', 'box1')], 
                          [('vacuum_object', 'arm2', 'cap1', 'box1'), ('vacuum_object', 'arm1', 'base1', 'box2')],
                          ...]
    '''

    cmd = 'timeout 1800 ./planners/optic-clp {} {} {} & echo $! >> {}/optic-clp-pid.txt'.format(args, domain, problem, pwd)

    ## call command ##
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
     
    (output, err) = process.communicate()
    # try:
    #     (output, err) = process.communicate(timeout=1800)
    # except subprocess.TimeoutExpired:
    #     if verbose == 2: print(color.fg_red('\n-- planning timeout (30m)'))
    #     return -1

    ## Wait for cmd to terminate. Get return returncode ##
    if process.wait() < 0: return -1

    ## bytes to string ##
    # shell = ''.join(map(chr, output))
    shell = to_str(output)

    if verbose == 2: 
        print(color.fg_voilet('\n-- planner stdout'))
        print(shell)
        if to_str(err):
            print(color.fg_voilet('-- planner stderr'))
            print(to_str(err))

    # Permission denied
    if 'Permission denied' in to_str(err):
        print(to_str(err))
        print(color.fg_voilet('-- run \'chmod +x planners/optic-clp\''))
        return -1

    ## if solution already exists in the problem ##
    if "has to terminate" in to_str(err) \
       or "error while loading shared libraries" in to_str(err) \
       or "Segmentation Fault" in shell:
        # print(color.fg_yellow("[planning failed due to some error in the pddl description]"))
        # print(color.fg_voilet('\n-- planner stdout'))
        # print(shell)
        # if to_str(err):
        #     print(color.fg_voilet('-- planner stderr'))
        #     print(to_str(err))
        # # exit()
        return -1

    ## if problem is unsolvable by EHC remove -b (activate best-first search)
    if "Problem unsolvable by EHC, and best-first search has been disabled" in shell:
        ## calling 'optic-clp' again removing '-b' option ##
        cmd = 'timeout 1800 ./planners/optic-clp -N {0} {1}'.format(domain, problem)
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
        (output, err) = process.communicate()
    # try:
    #     (output, err) = process.communicate(timeout=1800)
    # except subprocess.TimeoutExpired:
    #     if verbose == 2: print(color.fg_red('\n-- planning timeout (30m)'))
    #     return -1
        # shell = ''.join(map(chr, output))
        shell = to_str(output)

    ## if no solution exists try the next domain ##
    if "problem has been deemed unsolvable" in shell or "Problem unsolvable" in shell:
        return None

    ## if no solution exists try the next domain ##
    if "problem has been encountered, and the planner has to terminate" in to_str(err):
        if not verbose == 2: 
            print(color.fg_red('[error by external planner: run with \'-v 2\''))
        return None

    ## if solution already exists in the problem ##
    if ("; Plan empty" in shell and "; Plan found" in shell) \
        or "The empty plan is optimal" in shell:
        return list()

    ## refine the output screen and build a plan of actions' signatures ##

    # extract plan from ';<problem_name>' to 'Time:<value>'
    shell = shell[shell.find('; Time'):].strip()

    # split shell into a list of actions and ignore ';<problem_name>'
    shell = shell.split('\n')[1:]
    plan = OrderedDict()

    for action in shell:
        action = re.split('[, ) (]+', action)[:-1]
        plan.setdefault(action[0], []).append(tuple(action[1:]))

    # print(list(plan.values()))
    return list(plan.values())

###############################################################################
###############################################################################
## call madagascar (M) planner
def call_m(domain, problem, args='-P 1 -t 5 -N', pwd='/tmp', verbose=0):
    '''
    Call an external planner
    @domain : path to a given domain 
    @problem : path to a given problem 
    @verbose : if True, prints statistics before returning

    @return plan : the output plan is a list of actions as tuples, 
                   e.g., [[('move-car', 'l1', 'l4')], [('changetire', 'l4')]]
    '''
    cmd = 'timeout 1800 ./planners/m {0} {1} {2} -o {2}.soln & echo $! >> {3}/m-pid.txt'.format(args, domain, problem, pwd)

    ## call command ##
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn=os.setsid)

    (output, err) = process.communicate()
    # try:
    #     (output, err) = process.communicate(timeout=1800)
    # except subprocess.TimeoutExpired:
    #     if verbose == 2: print(color.fg_red('\n-- planning timeout (30m)'))
    #     return -1

    ## Wait for cmd to terminate. Get return returncode ##
    if process.wait() < 0: return -1

    ## bytes to string ##
    # shell = ''.join(map(chr, output))
    shell = to_str(output)

    if verbose == 2: 
        print(color.fg_voilet('\n-- planner stdout'))
        try: print('\n'+open(problem+'.soln').read())
        except: pass
        print(shell)
        if to_str(err):
            print(color.fg_voilet('-- planner stderr'))
            print(to_str(err))

    # Permission denied
    if 'Permission denied' in to_str(err):
        print(to_str(err))
        print(color.fg_voilet('-- run \'chmod +x planners/m\''))
        return -1

    ## if no solution exists try the next domain ##
    if "Timeout after" in shell:
        return None

    ## if solution already exists in the problem ##
    if "PLAN FOUND: 0 steps" in shell:
        return list()

    ## read the solution file
    plan = list()
    try:
        with open(problem+'.soln') as f:
            for line in enumerate(f):
                ## extract concurrent action at each step
                step = line[1].split()[2:]
                plan.append([tuple(re.split('[, ) (]+',s)[:-1]) for s in step])
    except: return -1

    return plan


###############################################################################
###############################################################################
## call probe planner
def call_probe(domain, problem, args='', pwd='/tmp', verbose=0):
    '''
    Call an external planner
    @domain : path to a given domain 
    @problem : path to a given problem 
    @verbose : if True, prints statistics before returning

    @return plan : the output plan is a list of actions as tuples, 
                   e.g., [[('move-car', 'l1', 'l4')], [('changetire', 'l4')]]
    '''
    cmd = 'timeout 1800 ./planners/probe {0} -d {1} -i {2} -o {2}.soln & echo $! >> {3}/prob-pid.txt'.format(args, domain, problem, pwd)

    ## call command ##
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn=os.setsid)

    (output, err) = process.communicate()
    # try:
    #     (output, err) = process.communicate(timeout=1800)
    # except subprocess.TimeoutExpired:
    #     if verbose == 2: print(color.fg_red('\n-- planning timeout (30m)'))
    #     return -1

    ## Wait for cmd to terminate. Get return returncode ##
    if process.wait() < 0: return -1

    ## bytes to string ##
    # shell = ''.join(map(chr, output))
    shell = to_str(output)

    if verbose == 2: 
        print(color.fg_voilet('\n-- planner stdout'))
        try: print('\n'+open(problem+'.soln.1').read())
        except: pass
        print(shell)
        if to_str(err):
            print(color.fg_voilet('-- planner stderr'))
            print(to_str(err))

    # Permission denied
    if "Permission denied" in to_str(err):
        print(to_str(err))
        print(color.fg_voilet('-- run \'chmod +x planners/m\''))
        return -1

    # unsupported features or syntax error
    if "syntax error" in to_str(err):
        return -1

    ## if no solution exists try the next domain ##
    if "Planning task not solvable" in shell or\
       "goal can be simplified to FALSE." in shell or\
       "Could not solve problem" in shell:
        return None

    ## read the solution file
    plan = list()
    try:
        with open(problem+'.soln.1') as f:
            for line in f:
                ## extract concurrent action at each step
                step = re.split('[, ) (]+',line.lower())[1:-1]
                plan.append([tuple(step)])
    except: return -1

    return plan


###############################################################################
###############################################################################
## call vhpop planner
def call_vhpop(domain, problem, args='-g -f DSep-LIFO -s HC -w 5 -l 1500000', pwd='/tmp', verbose=0):
    '''
    Call an external planner
    @domain : path to a given domain 
    @problem : path to a given problem 
    @verbose : if True, prints statistics before returning

    @return plan : the output plan is a list of actions as tuples, 
                   e.g., [[('move-car', 'l1', 'l4')], [('changetire', 'l4')]]
    '''
    cmd = 'timeout 1800 ./planners/vhpop {} {} {}  & echo $! >> {}/vhpop-pid.txt'.format(args, domain, problem, pwd)

    ## call command ##
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn=os.setsid)

    (output, err) = process.communicate()
    # try:
    #     (output, err) = process.communicate(timeout=1800)
    # except subprocess.TimeoutExpired:
    #     if verbose == 2: print(color.fg_red('\n-- planning timeout (30m)'))
    #     return -1

    ## Wait for cmd to terminate. Get return returncode ##
    if process.wait() < 0: return -1

    ## bytes to string ##
    # shell = ''.join(map(chr, output))
    shell = to_str(output)

    if verbose == 2: 
        print(color.fg_voilet('\n-- planner stdout'))
        print(shell)
        if to_str(err):
            print(color.fg_voilet('-- planner stderr'))
            print(to_str(err))

    # extract plan
    shell = shell[shell.find(';'):shell.find('Time')].strip()

    # Permission denied
    if 'Permission denied' in to_str(err):
        print(to_str(err))
        print(color.fg_voilet('-- run \'chmod +x planners/vhpop\''))
        return -1

    ## if not supported some PDDL features by planner ##
    if "undeclared type" in to_str(err) or\
       "type mismatch" in to_str(err) or\
       "syntax error" in to_str(err):
        # print(color.fg_yellow("[planning failed due to some error in the pddl description]"))
        # print(color.fg_voilet('\n-- planner stdout'))
        # print(shell)
        # if to_str(err):
        #     print(color.fg_voilet('-- planner stderr'))
        #     print(to_str(err))
        # exit()
        return -1

    ## if no solution exists try the next domain ##
    if ";Problem has no solution." in shell or "no plan" in shell or ";Search limit reached." in shell:
        return None

    # split shell into a list of actions and ignore '; Time'
    shell = shell.split('\n')[1:]

    plan = OrderedDict()

    for action in shell:
        action = re.split('[, ) (]+', action)[:-1]
        plan.setdefault(action[0], []).append(tuple(action[1:]))

    # print(list(plan.values()))
    return list(plan.values())


###############################################################################
###############################################################################
## call lpg-td planner
def call_lpg_td(domain, problem, args='-speed -noout', pwd='/tmp', verbose=0):
    '''
    Call an external planner
    @domain : path to a given domain 
    @problem : path to a given problem 
    @verbose : if True, prints statistics before returning

    @return plan : the output plan is a list of actions as tuples, 
                   e.g., [[('move_to_grasp', 'arm1', 'box1', 'base1', 'box2'), ('move_to_grasp', 'arm2', 'box2', 'cap1', 'box1')], 
                          [('vacuum_object', 'arm2', 'cap1', 'box1'), ('vacuum_object', 'arm1', 'base1', 'box2')],
                          ...]
    '''
    cmd = 'timeout 1800 ./planners/lpg-td -o {} -f {} {} & echo $! >> {}/lpg-td-pid.txt'.format(domain, problem, args, pwd)

    ## call command ##
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
     
    (output, err) = process.communicate()
    # try:
    #     (output, err) = process.communicate(timeout=1800)
    # except subprocess.TimeoutExpired:
    #     if verbose == 2: print(color.fg_red('\n-- planning timeout (30m)'))
    #     return -1

    ## Wait for cmd to terminate. Get return returncode ##
    if process.wait() < 0: return -1

    ## bytes to string ##
    # shell = ''.join(map(chr, output))
    shell = to_str(output)

    if verbose == 2: 
        print(color.fg_voilet('\n-- planner stdout'))
        print(shell)
        if to_str(err):
            print(color.fg_voilet('-- planner stderr'))
            print(to_str(err))

    # Permission denied
    if 'Permission denied' in to_str(err):
        print(to_str(err))
        print(color.fg_voilet('-- run \'chmod +x planners/lpg-td\''))
        return -1

    ## if no solution exists try the next domain ##
    if "Goals of the planning problem can not be reached." in shell \
        or "goal can be simplified to FALSE" in shell \
        or "The problem is unsolvable" in shell \
        or "No plan will solve it" in shell:
        return None

    ## if not supported some PDDL features by planner ##
    if "not supported by this exp version" in to_str(err) \
       or "type mismatch" in shell \
       or "Segmentation Fault" in shell:
        # print(color.fg_yellow("[planning failed due to some error in the pddl description]"))
        # print(color.fg_voilet('\n-- planner stdout'))
        # print(shell)
        # if to_str(err):
        #     print(color.fg_voilet('-- planner stderr'))
        #     print(to_str(err))
        # exit()
        return -1

    ## if solution already exists in the problem ##
    if "No action in solution" in shell and "Plan computed:" in shell:
        return list()

    ## refine the output screen and build a plan of actions' signatures ##

    # extract plan from ';<problem_name>' to 'Time:<value>'
    shell = shell[shell.find('Time: (ACTION) [action Duration; action Cost]'):shell.rfind('Solution found:')].strip()

    # split shell into a list of actions and ignore ';<problem_name>'
    shell = shell.lower().split('\n')[1:]

    plan = OrderedDict()

    for action in shell:
        action = re.split('[, ) (]+', action)[1:-2]
        plan.setdefault(action[0], []).append(tuple(action[1:]))

    # print(list(plan.values()))
    return list(plan.values())


###############################################################################
###############################################################################
## call lpg planner
def call_lpg(domain, problem, args='-n 1', pwd='/tmp', verbose=0):
    '''
    Call an external planner
    @domain : path to a given domain 
    @problem : path to a given problem 
    @verbose : if True, prints statistics before returning

    @return plan : the output plan is a list of actions as tuples, 
                   e.g., [[('move_to_grasp', 'arm1', 'box1', 'base1', 'box2'), ('move_to_grasp', 'arm2', 'box2', 'cap1', 'box1')], 
                          [('vacuum_object', 'arm2', 'cap1', 'box1'), ('vacuum_object', 'arm1', 'base1', 'box2')],
                          ...]
    '''
    cmd = 'timeout 1800 ./planners/lpg -o {} -f {} {} & echo $! >> {}/lpg-pid.txt'.format(domain, problem, args, pwd)

    ## call command ##
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
     
    (output, err) = process.communicate()
    # try:
    #     (output, err) = process.communicate(timeout=1800)
    # except subprocess.TimeoutExpired:
    #     if verbose == 2: print(color.fg_red('\n-- planning timeout (30m)'))
    #     return -1

    ## Wait for cmd to terminate. Get return returncode ##
    if process.wait() < 0: return -1

    ## bytes to string ##
    # shell = ''.join(map(chr, output))
    shell = to_str(output)

    if verbose == 2: 
        print(color.fg_voilet('\n-- planner stdout'))
        print(shell)
        if to_str(err):
            print(color.fg_voilet('-- planner stderr'))
            print(to_str(err))

    # Permission denied
    if 'Permission denied' in to_str(err):
        print(to_str(err))
        print(color.fg_voilet('-- run \'chmod +x planners/lpg\''))
        return -1

    ## if no solution exists try the next domain ##
    if "Goals of the planning problem can not be reached." in shell \
        or "goal can be simplified to FALSE" in shell \
        or "The problem is unsolvable" in shell \
        or "No plan will solve it" in shell:
        return None

    ## if not supported some PDDL features by planner ##
    if "not supported by this exp version" in shell \
       or "type mismatch" in shell \
       or "Unexpected node:" in shell \
       or "Segmentation Fault" in shell \
       or "syntax error" in str(err):
        # print(color.fg_yellow("[planning failed due to some error in the pddl description]"))
        # print(color.fg_voilet('\n-- planner stdout'))
        # print(shell)
        # if to_str(err):
        #     print(color.fg_voilet('-- planner stderr'))
        #     print(to_str(err))
        # exit()
        return -1

    ## if solution already exists in the problem ##
    if "No action in solution" in shell and "Plan computed:" in shell:
        return list()

    ## refine the output screen and build a plan of actions' signatures ##

    # extract plan from ';<problem_name>' to 'Time:<value>'
    shell = shell[shell.find('Time: (ACTION) [action Duration; action Cost]'):shell.rfind('Solution number:')].strip()

    # split shell into a list of actions and ignore ';<problem_name>'
    shell = shell.lower().split('\n')[1:]

    plan = OrderedDict()

    for action in shell:
        action = re.split('[, ) (]+', action)[1:-2]
        plan.setdefault(action[0], []).append(tuple(action[1:]))

    # print(list(plan.values()))
    return list(plan.values())


###############################################################################
###############################################################################
## call fast-downward planner
def call_fd(domain, problem, args='--search "astar(lmcut())"', pwd='/tmp', verbose=0):
    '''
    Call an external planner
    @domain : path to a given domain 
    @problem : path to a given problem 
    @verbose : if True, prints statistics before returning

    @return plan : the output plan is a list of actions as tuples, 
                   e.g., [[('move_to_grasp', 'arm1', 'box1', 'base1', 'box2'), ('move_to_grasp', 'arm2', 'box2', 'cap1', 'box1')], 
                          [('vacuum_object', 'arm2', 'cap1', 'box1'), ('vacuum_object', 'arm1', 'base1', 'box2')],
                          ...]
    '''
    cmd = 'timeout 1800 ./planners/fd/fast-downward.py --search-memory-limit 4G --sas-file /tmp/output.sas --plan-file /tmp/plan.txt {} {} {} & echo $! >> {}/fd-pid.txt'.format(domain, problem, args, pwd)

    ## call command ##
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
     
    (output, err) = process.communicate()
    # try:
    #     (output, err) = process.communicate(timeout=1800)
    # except subprocess.TimeoutExpired:
    #     if verbose == 2: print(color.fg_red('\n-- planning timeout (30m)'))
    #     return -1

    ## Wait for cmd to terminate. Get return returncode ##
    if process.wait() < 0: return -1

    ## bytes to string ##
    # shell = ''.join(map(chr, output))
    shell = to_str(output)

    if verbose == 2: 
        print(color.fg_voilet('\n-- planner stdout'))
        print(shell)
        if to_str(err):
            print(color.fg_voilet('-- planner stderr'))
            print(to_str(err))

    ## if there is shared library errors ##
    if "error while loading shared libraries" in to_str(err):
        return -1

    # Permission denied
    if 'Permission denied' in to_str(err):
        print(to_str(err))
        print(color.fg_voilet('-- run \'chmod +x planners/fd/fast-downward.py\''))
        return -1

    ## if no solution exists try the next domain ##
    if not "translate exit code: 0" in shell or\
           "configuration does not support" in to_str(err):
        # if not verbose:
        #     print(color.fg_voilet('-- \'fd\' does not support this pddl configuration -- run with \'-v 2\''))
        return -1

    ## problem proved unsolvable ##
    if "search exit code: 11" in shell or "search exit code: 12" in shell:
        return None

    ## if no solution exists try the next domain ##
    if not "search exit code: 0" in shell:
        return -1

    ## read the solution file
    plan = list()
    try:
        with open('/tmp/plan.txt') as f:
            for line in f:
                ## extract concurrent action at each step
                if '; cost =' in line: continue
                step = re.split('[, ) (]+',line)[1:-1]
                plan.append([tuple(step)])
    except FileNotFoundError as fnf_error:
        print(shell)
        # exit()
        return -1

    return plan


###############################################################################
###############################################################################
## checks the output type and convert it to str
## in python 3 is of type 'byte' and in 2 is of type 'str' already
def to_str(output):

    if output is None: return str()

    ## bytes to string (Python 3) ##
    if sys.version_info[0] > 2:
        return ''.join(map(chr, output))

    ## already in string ##
    return str(output)

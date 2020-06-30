
from multiprocessing import Pool, Array
import subprocess, os, sys, re, signal
from collections import OrderedDict
from color import fg_green, fg_red, fg_yellow, fg_blue, fg_voilet, fg_beige, bg_green, bg_red, bg_yellow, bg_blue, bg_voilet

args_profiles = {
    'ff'        : { 0 : '' },
    'm'         : { 0 : '-P 0 -N -m 4096', \
                    1 : '-P 1 -N -m 4096' },
    'optic-clp' : { 0 : '-b -N' },
    'lpg-td'    : { 0 : '-speed -noout', \
                    1 : '-quality -v off -noout' },
    'lpg'       : { 0 : '-n 1 -noout' },
    'vhpop'     : { 0 : '-g -f DSep-LIFO -s HC -w 5 -l 1500000' },
    'fd'        : { 0 : '--search "astar(lmcut())"', \
                    1 : '--evaluator "hff=ff()" --evaluator "hcea=cea()" --search "lazy_greedy([hff, hcea], preferred=[hff, hcea])"'}
}

# stores the pid of 'Popen' calls to external planners
pid_lst = Array('I', len(os.listdir('planners')))

def check_pid(pid):        
    """check if a subprocess is running"""
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True

def kill_pid(pid):
    '''kill a subprocess by pid'''
    # check if it is running first
    if pid == 0: return 0
    try:
        os.killpg(pid, 0)
    except OSError:
        return 0
    # kill it if it is still running
    try:
        os.killpg(pid, signal.SIGKILL)
    except OSError:
        return 0
    return 0

###############################################################################
###############################################################################
class Plan():
    '''
    creates a planner object and calls multiple planners
    to solve a given problem and returns and terminates
    as soon as the first planner finds a plan
    '''
    def __init__(self, planners, domain, problem, verbose):
        self.plan = None
        self.planners = planners
        # if only one planner then no need multiprocessing
        if len(set(planners)) == 1:
            try:
                self.plan = call_planner(planners[0], domain, problem, args_profiles[planners[0]][0], verbose)
            except KeyboardInterrupt:
                # kill also the running planner
                pid_lst[0] = kill_pid(pid_lst[0])
                raise
            if self.plan == -1:
                if not verbose: 
                    print(fg_red('[some error by external planner -- run again with parameter \'-v 2\']'))
                sys.exit(0)
            return

        # otherwise, run in multiprocessing
        self.pool = Pool(processes=len(planners))
        for pidx, planner in enumerate(self.planners):
            self.pool.apply_async(call_planner, \
                args=(planner, domain, problem, args_profiles[planner][0], verbose, pidx), \
                callback=self.callback)
        self.pool.close()
        try:
            self.pool.join()
        except KeyboardInterrupt:
            self.pool.terminate()
            # kill also running planners
            for i in range(len(self.planners)):
                pid_lst[i] = kill_pid(pid_lst[i])
            raise

    def callback(self, plan):
        # if plan == -1:
        #     print(plan)
        #     # Check if other planners are still running
        #     s = len(self.planners)
        #     for i in range(len(self.planners)):
        #         try:
        #             os.killpg(pid_lst[i], 0)
        #         except OSError:
        #             s -= 1
        #     # all planners failed
        #     if s == 0:
        #         if not verbose: 
        #             print(fg_red('[all planners failed: run again with parameter \'-v 2\''))
        #         sys.exit(0)
        # else:
        if not plan == -1:
            self.plan = plan
            self.pool.terminate()
            # kill other running planners
            for i in range(len(self.planners)):
                pid_lst[i] = kill_pid(pid_lst[i])

    # cleanup the child process if the main process was suddenly killed/crashed
    def __del__(self): 
        # kill the running planners
        for i in range(len(self.planners)):
            pid_lst[i] = kill_pid(pid_lst[i])

###############################################################################
###############################################################################
def call_planner(planner='ff', domain=None, problem=None, args='', verbose=0, pidx=0):
    '''
    Call an external deterministic planner.
    Arguments:
    @domain : path to a given domain 
    @problem : path to a given problem 
    @planner : the name of the external planner  
    @verbose : if True, prints statistics before returning
    @pidx : the process index for using the shared array 'pid_lst'
    '''
    ## FF planner ##
    if 'ff' in planner.lower():
        return call_ff(domain, problem, args, verbose, pidx)

    ## Madagascar (M) planner ##
    elif 'm' in planner.lower():
        return call_m(domain, problem, args, verbose, pidx)

    ## optic-clp planner ##
    elif 'optic-clp' in planner.lower() or 'optic' in planner.lower():
        return call_optic_clp(domain, problem, args, verbose, pidx)

    ## optic-clp planner ##
    elif 'vhpop' in planner.lower():
        return call_vhpop(domain, problem, args, verbose, pidx)

    ## lpg-td planner ##
    elif 'lpg-td' in planner.lower():
        return call_lpg_td(domain, problem, args, verbose, pidx)

    ## lpg-td planner ##
    elif 'lpg' in planner.lower():
        return call_lpg(domain, problem, args, verbose, pidx)

    ## lpg-td planner ##
    elif 'fd' in planner.lower():
        return call_fd(domain, problem, args, verbose, pidx)

    ## no planner ##
    else:
        print(fg_red("\n[There is not yet a function for parsing the outputs of '{0}'!]\n".format(planner)))
        # exit()
        return -1


###############################################################################
###############################################################################
## call ff planner
def call_ff(domain, problem, args='', verbose=0, pidx=0):
    '''
    Call an external planner
    @domain : path to a given domain 
    @problem : path to a given problem 
    @verbose : if True, prints statistics before returning

    @return plan : the output plan is a list of actions as tuples, 
                   e.g., [[('move-car', 'l1', 'l4')], [('changetire', 'l4')]]
    '''

    cmd = './planners/ff -o {} -f {} {}'.format(domain, problem, args)

    ## call command ##
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn=os.setsid)

    # add the pid into pid_lst 
    pid_lst[pidx] = process.pid

    (output, err) = process.communicate()
     
    ## Wait for cmd to terminate. Get return returncode ##
    # p_status = process.wait()
    # print("Command exit status/return code : ", p_status)

    ## bytes to string ##
    # shell = ''.join(map(chr, output))
    shell = to_str(output)

    if verbose == 2: 
        print(fg_voilet('\n-- planner stdout'))
        print(shell)
        if to_str(err):
            print(fg_voilet('-- planner stderr'))
            print(to_str(err))

    # Permission denied
    if 'Permission denied' in to_str(err):
        print(to_str(err))
        print(fg_voilet('-- run \'chmod +x planners/ff\''))
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
       'too many constants!' in shell or 'syntax error in line' in to_str(err):
        # print(fg_yellow('[planning failed due to some error in the pddl description]'))
        # print(fg_voilet('\n-- planner stdout'))
        # print(shell)
        # if to_str(err):
        #     print(fg_voilet('-- planner stderr'))
        #     print(to_str(err))
        # exit()
        return -1

    ## refine the output screen and build a plan of actions' signatures ##
    shell = shell[shell.find('step')+len('step'):shell.rfind('time spent')].strip()  # extract plan

    return [[tuple(l.lower().split()[1:])] for l in shell.splitlines()]  # string to list of tuples

###############################################################################
###############################################################################
## call optic-clp planner
def call_optic_clp(domain, problem, args='-b -N', verbose=0, pidx=0):
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

    cmd = './planners/optic-clp {} {} {}'.format(args, domain, problem)

    ## call command ##
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
     
    # add the pid into pid_lst 
    pid_lst[pidx] = process.pid

    (output, err) = process.communicate()

    ## Wait for cmd to terminate. Get return returncode ##
    # p_status = process.wait()
    # print("Command exit status/return code : ", p_status)

    ## bytes to string ##
    # shell = ''.join(map(chr, output))
    shell = to_str(output)

    if verbose == 2: 
        print(fg_voilet('\n-- planner stdout'))
        print(shell)
        if to_str(err):
            print(fg_voilet('-- planner stderr'))
            print(to_str(err))

    # Permission denied
    if 'Permission denied' in to_str(err):
        print(to_str(err))
        print(fg_voilet('-- run \'chmod +x planners/optic-clp\''))
        return -1

    ## if solution already exists in the problem ##
    if "has to terminate" in to_str(err):
        # print(fg_yellow("[planning failed due to some error in the pddl description]"))
        # print(fg_voilet('\n-- planner stdout'))
        # print(shell)
        # if to_str(err):
        #     print(fg_voilet('-- planner stderr'))
        #     print(to_str(err))
        # # exit()
        return -1

    ## if problem is unsolvable by EHC remove -b (activate best-first search)
    if "Problem unsolvable by EHC, and best-first search has been disabled":
        ## calling 'optic-clp' again removing '-b' option ##
        cmd = './planners/optic-clp -N {0} {1}'.format(domain, problem)
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
        (output, err) = process.communicate()
        # shell = ''.join(map(chr, output))
        shell = to_str(output)

    ## if no solution exists try the next domain ##
    if "problem has been deemed unsolvable" in shell or "Problem unsolvable" in shell:
        return None

    ## if no solution exists try the next domain ##
    if "file appear to violate part of the PDDL" in to_str(err) or\
       "problem has been encountered, and the planner has to terminate" in to_str(err):
        if not verbose == 2: 
            print(fg_red('[error by external planner: run with \'-v 2\''))
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
def call_m(domain, problem, args='-P 1 -t 5 -N', verbose=0, pidx=0):
    '''
    Call an external planner
    @domain : path to a given domain 
    @problem : path to a given problem 
    @verbose : if True, prints statistics before returning

    @return plan : the output plan is a list of actions as tuples, 
                   e.g., [[('move-car', 'l1', 'l4')], [('changetire', 'l4')]]
    '''
    cmd = './planners/m {0} {1} {2} -o {2}.soln'.format(args, domain, problem)

    ## call command ##
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn=os.setsid)

    # add the pid into pid_lst 
    pid_lst[pidx] = process.pid

    (output, err) = process.communicate()

    ## Wait for cmd to terminate. Get return returncode ##
    # p_status = process.wait()
    # print("Command exit status/return code : ", p_status)

    ## bytes to string ##
    # shell = ''.join(map(chr, output))
    shell = to_str(output)

    if verbose == 2: 
        print(fg_voilet('\n-- planner stdout'))
        print('\n'+open(problem+'.soln').read())
        print(shell)
        if to_str(err):
            print(fg_voilet('-- planner stderr'))
            print(to_str(err))

    # Permission denied
    if 'Permission denied' in to_str(err):
        print(to_str(err))
        print(fg_voilet('-- run \'chmod +x planners/m\''))
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
    except FileNotFoundError as fnf_error:
        print(shell)
        # exit()
        return -1

    return plan


###############################################################################
###############################################################################
## call vhpop planner
def call_vhpop(domain, problem, args='-g -f DSep-LIFO -s HC -w 5 -l 1500000', verbose=0, pidx=0):
    '''
    Call an external planner
    @domain : path to a given domain 
    @problem : path to a given problem 
    @verbose : if True, prints statistics before returning

    @return plan : the output plan is a list of actions as tuples, 
                   e.g., [[('move-car', 'l1', 'l4')], [('changetire', 'l4')]]
    '''
    cmd = './planners/vhpop {} {} {}'.format(args, domain, problem)

    ## call command ##
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn=os.setsid)

    # add the pid into pid_lst 
    pid_lst[pidx] = process.pid

    (output, err) = process.communicate()

    ## Wait for cmd to terminate. Get return returncode ##
    # p_status = process.wait()
    # print("Command exit status/return code : ", p_status)

    ## bytes to string ##
    # shell = ''.join(map(chr, output))
    shell = to_str(output)

    if verbose == 2: 
        print(fg_voilet('\n-- planner stdout'))
        print(shell)
        if to_str(err):
            print(fg_voilet('-- planner stderr'))
            print(to_str(err))

    # extract plan
    shell = shell[shell.find(';'):shell.find('Time')].strip()

    # Permission denied
    if 'Permission denied' in to_str(err):
        print(to_str(err))
        print(fg_voilet('-- run \'chmod +x planners/vhpop\''))
        return -1

    ## if not supported some PDDL features by planner ##
    if "undeclared type" in to_str(err) or\
       "type mismatch" in to_str(err):
        # print(fg_yellow("[planning failed due to some error in the pddl description]"))
        # print(fg_voilet('\n-- planner stdout'))
        # print(shell)
        # if to_str(err):
        #     print(fg_voilet('-- planner stderr'))
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
def call_lpg_td(domain, problem, args='-speed -noout', verbose=0, pidx=0):
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
    cmd = './planners/lpg-td -o {} -f {} {}'.format(domain, problem, args)

    ## call command ##
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
     
    # add the pid into pid_lst 
    pid_lst[pidx] = process.pid

    (output, err) = process.communicate()

    ## Wait for cmd to terminate. Get return returncode ##
    # p_status = process.wait()
    # print("Command exit status/return code : ", p_status)

    ## bytes to string ##
    # shell = ''.join(map(chr, output))
    shell = to_str(output)

    if verbose == 2: 
        print(fg_voilet('\n-- planner stdout'))
        print(shell)
        if to_str(err):
            print(fg_voilet('-- planner stderr'))
            print(to_str(err))

    # Permission denied
    if 'Permission denied' in to_str(err):
        print(to_str(err))
        print(fg_voilet('-- run \'chmod +x planners/lpg-td\''))
        return -1

    ## if no solution exists try the next domain ##
    if "Goals of the planning problem can not be reached." in shell \
        or "goal can be simplified to FALSE" in shell \
        or "The problem is unsolvable" in shell \
        or "No plan will solve it" in shell:
        return None

    ## if not supported some PDDL features by planner ##
    if "not supported by this exp version" in to_str(err) or\
       "type mismatch" in shell:
        # print(fg_yellow("[planning failed due to some error in the pddl description]"))
        # print(fg_voilet('\n-- planner stdout'))
        # print(shell)
        # if to_str(err):
        #     print(fg_voilet('-- planner stderr'))
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
def call_lpg(domain, problem, args='-n 1', verbose=0, pidx=0):
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
    cmd = './planners/lpg -o {} -f {} {}'.format(domain, problem, args)

    ## call command ##
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
     
    # add the pid into pid_lst 
    pid_lst[pidx] = process.pid

    (output, err) = process.communicate()

    ## Wait for cmd to terminate. Get return returncode ##
    # p_status = process.wait()
    # print("Command exit status/return code : ", p_status)

    ## bytes to string ##
    # shell = ''.join(map(chr, output))
    shell = to_str(output)

    if verbose == 2: 
        print(fg_voilet('\n-- planner stdout'))
        print(shell)
        if to_str(err):
            print(fg_voilet('-- planner stderr'))
            print(to_str(err))

    # Permission denied
    if 'Permission denied' in to_str(err):
        print(to_str(err))
        print(fg_voilet('-- run \'chmod +x planners/lpg\''))
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
       or "Unexpected node:" in shell:
        # print(fg_yellow("[planning failed due to some error in the pddl description]"))
        # print(fg_voilet('\n-- planner stdout'))
        # print(shell)
        # if to_str(err):
        #     print(fg_voilet('-- planner stderr'))
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
def call_fd(domain, problem, args='--search "astar(lmcut())"', verbose=0, pidx=0):
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
    cmd = './planners/fd/fast-downward.py --search-memory-limit 4G --sas-file /tmp/output.sas --plan-file /tmp/plan.txt {} {} {}'.format(domain, problem, args)

    ## call command ##
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
     
    # add the pid into pid_lst 
    pid_lst[pidx] = process.pid

    (output, err) = process.communicate()

    ## Wait for cmd to terminate. Get return returncode ##
    # p_status = process.wait()
    # print("Command exit status/return code : ", p_status)

    ## bytes to string ##
    # shell = ''.join(map(chr, output))
    shell = to_str(output)

    if verbose == 2: 
        print(fg_voilet('\n-- planner stdout'))
        print(shell)
        if to_str(err):
            print(fg_voilet('-- planner stderr'))
            print(to_str(err))

    # Permission denied
    if 'Permission denied' in to_str(err):
        print(to_str(err))
        print(fg_voilet('-- run \'chmod +x planners/fd/fast-downward.py\''))
        return -1

    ## if no solution exists try the next domain ##
    if not "translate exit code: 0" in shell or\
           "configuration does not support" in to_str(err):
        # if not verbose:
        #     print(fg_voilet('-- \'fd\' does not support this pddl configuration -- run with \'-v 2\''))
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

    ## bytes to string ##
    if sys.version_info[0] > 2:
        return ''.join(map(chr, output))

    ## already in string ##
    return str(output)

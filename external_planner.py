
import subprocess, os, sys, re, io
from subprocess import check_output
from collections import OrderedDict
from color import fg_green, fg_red, fg_yellow, fg_blue, fg_voilet, fg_beige, bg_green, bg_red, bg_yellow, bg_blue, bg_voilet


###############################################################################
###############################################################################
## call ff planner
def call_ff(domain, problem, verbose=0):
    """
    Call an external planner
    @arg domain : path to a given domain 
    @arg problem : path to a given problem 
    @arg verbose : if True, prints statistics before returning

    @return plan : the output plan is a list of actions as tuples, 
                   e.g., [[('move-car', 'l1', 'l4')], [('changetire', 'l4')]]
    """

    cmd = './planners/ff -o {0} -f {1}'.format(domain, problem)

    ## call command ##
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
     
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

    ## if no solution exists try the next domain ##
    if "goal can be simplified to FALSE" in shell or "problem proven unsolvable" in shell:
        return None

    ## if solution already exists in the problem ##
    if "goal can be simplified to TRUE" in shell:
        return list()

    ## if solution already exists in the problem ##
    if "undeclared predicate" in shell:
        print("[planning failed due to some errors in the domain description (see below)]\n")
        print(shell)
        exit()

    ## refine the output screen and build a plan of actions' signatures ##
    shell = shell[shell.find('step')+len('step'):shell.rfind('time spent')].strip()  # extract plan

    return [[tuple(l.lower().split()[1:])] for l in shell.splitlines()]  # string to list of tuples

###############################################################################
###############################################################################
## call optic-clp planner
def call_optic_clp(domain, problem, verbose=0):
    """
    Call an external planner
    @arg domain : path to a given domain 
    @arg problem : path to a given problem 
    @arg verbose : if True, prints statistics before returning

    @return plan : the output plan is a list of actions as tuples, 
                   e.g., [[('move_to_grasp', 'arm1', 'box1', 'base1', 'box2'), ('move_to_grasp', 'arm2', 'box2', 'cap1', 'box1')], 
                          [('vacuum_object', 'arm2', 'cap1', 'box1'), ('vacuum_object', 'arm1', 'base1', 'box2')],
                          ...]
    """

    cmd = './planners/optic-clp -b -N {0} {1}'.format(domain, problem)

    ## call command ##
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
     
    (output, err) = process.communicate()

    # output = check_output(["./planners/optic-clp", "-b", "-N", domain, problem])
     
    ## Wait for cmd to terminate. Get return returncode ##
    # p_status = process.wait()
    # print("Command exit status/return code : ", p_status)

    ## bytes to string ##
    # shell = ''.join(map(chr, output))
    shell = to_str(output)

    ## if problem is unsolvable by EHC remove -b (activate best-first search)
    if "Problem unsolvable by EHC, and best-first search has been disabled":
        ## calling 'optic-clp' again removing '-b' option ##
        cmd = './planners/optic-clp -N {0} {1}'.format(domain, problem)
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (output, err) = process.communicate()
        # shell = ''.join(map(chr, output))
        shell = to_str(output)

    if verbose == 2: 
        print(fg_voilet('\n-- planner stdout'))
        print(shell)
        if to_str(err):
            print(fg_voilet('-- planner stderr'))
            print(to_str(err))

    ## if no solution exists try the next domain ##
    if "problem has been deemed unsolvable" in shell or "Problem unsolvable" in shell:
        return None

    ## if solution already exists in the problem ##
    if ("; Plan empty" in shell and "; Plan found" in shell) \
        or "The empty plan is optimal" is shell:
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
def call_m(domain, problem, verbose=0):
    """
    Call an external planner
    @arg domain : path to a given domain 
    @arg problem : path to a given problem 
    @arg verbose : if True, prints statistics before returning

    @return plan : the output plan is a list of actions as tuples, 
                   e.g., [[('move-car', 'l1', 'l4')], [('changetire', 'l4')]]
    """

    cmd = './planners/m -P 1 -t 5 {0} {1} -o {1}.soln'.format(domain, problem)


    ## call command ##
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    (output, err) = process.communicate()

    # s = str()
    # for out in run(cmd):
    #     s+=out

    ## Wait for cmd to terminate. Get return returncode ##
    # p_status = process.wait()
    # print("Command exit status/return code : ", p_status)

    ## bytes to string ##
    # shell = ''.join(map(chr, output))
    shell = to_str(output)

    ## if no solution exists try the next domain ##
    if "Timeout after" in shell:
        return None

    ## if solution already exists in the problem ##
    if "PLAN FOUND: 0 steps" in shell:
        return list()

    ## read the probabilistic actions names
    plan = list()
    try:
        with open(problem+'.soln') as f:
            for line in enumerate(f):
                ## extract concurrent action at each step
                step = line[1].split()[2:]
                plan.append([tuple(re.split('[, ) (]+',s)[:-1]) for s in step])
    except FileNotFoundError as fnf_error:
        print(shell)
        exit()

    if verbose == 2: 
        print(fg_voilet('\n-- planner stdout'))
        print('\n'+open(problem+'.soln').read())
        print(shell)
        if to_str(err):
            print(fg_voilet('-- planner stderr'))
            print(to_str(err))

    return plan


###############################################################################
###############################################################################
## call vhpop planner
def call_vhpop(domain, problem, verbose=0):
    """
    Call an external planner
    @arg domain : path to a given domain 
    @arg problem : path to a given problem 
    @arg verbose : if True, prints statistics before returning

    @return plan : the output plan is a list of actions as tuples, 
                   e.g., [[('move-car', 'l1', 'l4')], [('changetire', 'l4')]]
    """

    cmd = './planners/vhpop -g -f DSep-LIFO -s HC -w 5 -l 1500000 {0} {1}'.format(domain, problem)


    ## call command ##
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    (output, err) = process.communicate()

    # s = str()
    # for out in run(cmd):
    #     s+=out

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
def call_lpg_td(domain, problem, verbose=0):
    """
    Call an external planner
    @arg domain : path to a given domain 
    @arg problem : path to a given problem 
    @arg verbose : if True, prints statistics before returning

    @return plan : the output plan is a list of actions as tuples, 
                   e.g., [[('move_to_grasp', 'arm1', 'box1', 'base1', 'box2'), ('move_to_grasp', 'arm2', 'box2', 'cap1', 'box1')], 
                          [('vacuum_object', 'arm2', 'cap1', 'box1'), ('vacuum_object', 'arm1', 'base1', 'box2')],
                          ...]
    """

    cmd = './planners/lpg-td -o {0} -f {1} -speed -noout'.format(domain, problem)

    ## call command ##
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
     
    (output, err) = process.communicate()

    # output = check_output(["./planners/optic-clp", "-b", "-N", domain, problem])
     
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

    ## if no solution exists try the next domain ##
    if "Goals of the planning problem can not be reached." in shell \
        or "goal can be simplified to FALSE" in shell \
        or "No plan will solve it" in shell:
        return None

    ## if not supported some PDDL features by planner ##
    if "not supported by this exp version" in to_str(err):
        if not verbose == 2: 
            print('\nSome PDDL features not supported by this planner.')
            print('Please try to run with \'-v 2\' to see the planners output.\n')
        exit()

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
## capture realtime output from a shell command
def run(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)

    # for line in io.TextIOWrapper(process.stdout, encoding="utf-8"): 
    #     print(line.strip())

    # while True:
    #     line = process.stdout.readline().rstrip()
    #     # if not line:
    #     if "Emitting top-level constant FALSE" in line.strip().decode():
    #         break
    #     yield line
    # print(process.stdout)
    while True:
        print('read')
        output = process.stdout.readline().rstrip().decode()
        # output = ''.join(map(chr, output))
        # print(output.decode(),process.poll())
        if "Emitting top-level constant FALSE" in output and process.poll() is None:
            break
        if not output and process.poll() is not None:
            break
        yield output
    # rc = process.poll()
    # return rc


###############################################################################
###############################################################################
def call_planner(domain, problem, planner='ff', verbose=0):
    """
    Call an external deterministic planner.
    Arguments:
    @arg domain : path to a given domain 
    @arg problem : path to a given problem 
    @arg planner : the name of the external planner  
    @arg verbose : if True, prints statistics before returning
    """

    Planners = os.listdir('planners')

    if planner.lower().split('/')[-1] not in map(str.lower, Planners):
        print(fg_red("\n'{0}' does not exist in 'planners/' directory!".format(planner)))
        print(fg_yellow("currently these planners are available: ") + str(Planners))
        exit()

    ## FF planner ##
    if 'ff' in planner.lower():
        return call_ff(domain, problem, verbose)

    ## Madagascar (M) planner ##
    elif 'm' in planner.lower():
        return call_m(domain, problem, verbose)

    ## optic-clp planner ##
    elif 'optic-clp' in planner.lower() or 'optic' in planner.lower():
        return call_optic_clp(domain, problem, verbose)

    ## optic-clp planner ##
    elif 'vhpop' in planner.lower():
        return call_vhpop(domain, problem, verbose)

    ## lpg-td planner ##
    elif 'lpg-td' in planner.lower():
        return call_lpg_td(domain, problem, verbose)

    ## optic-clp planner ##
    else:
        print(fg_red("\n[There is not yet a function for parsing the outputs of '{0}'!]\n".format(planner)))
        exit()


## checks the output type and convert it to str
## in python 3 is of type 'byte' and in 2 is of type 'str' already
def to_str(output):

    ## bytes to string ##
    if sys.version_info[0] > 2:
        return ''.join(map(chr, output))

    ## already in string ##
    return str(output)
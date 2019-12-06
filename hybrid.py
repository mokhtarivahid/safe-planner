    ## loop until goal is achieved
    while not state.is_true(*(problem.goals, problem.num_goals)):

        ## create a pddl problem given the current state
        problem_pddl = problem.pddl(state, goals)

        ## print out some info
        if args.verbose: print(fg_yellow('@ problem:'), problem_pddl)

        ## call planner to make a plan given the domain, problem and planner
        # policy = Planner(args.domain, problem_pddl, args.planner, args.verbose)
        policy = Planner(args.domain, problem_pddl, args.planner)

        ## print out the policy
        if args.verbose: policy.print_plan()

        ## accumulate the planning calls
        planning_call += 1

        ## translate the policy into a cyclic contingency plan (tree)
        plan = policy.plan()


def is_reachable_mat(action_name, action_args):
    return str(action_name+action_args)


def simulate(plan, verbose=False):
    ''' simulate the execution of the (cyclic contingency) plan 
        and refine it in case of any geometric limitation
    '''

    # output refined plan
    refined_plan = OrderedDict()

    ## start from level 0
    level = 0

    ## loop until goal is achieved
    while not plan[level] == 'goal':

        ## print out the level
        if verbose: print('@ level', level)

        ## pick the current step of actions
        step = plan[level]

        if step == 'goal':
            # goal state is achieved
            print(fg_voilet('@ goal'))
            break                

        elif step == None:
            # normally shouldn't happen; otherwise, something is wrong (report it if happened)
            # anyway, it makes the plan a weak solution
            print(bg_voilet('None!'))
            print(bg_beige('plan gets an unsafe situation!'))
            print(bg_beige('normally should not happen; report it if please!'))
            print(bg_beige('anyhow the current plan is a weak solution!'))
            break
        else:
            # unfold step into a tuple of actions and outcomes
            (actions, outcomes) = step

            ## break every action into its name and args in a list
            actions_list = [(action.sig[0], action.sig[1:]) for action in actions]

            ## call matlab code to execute the action
            ## check if the object is reachable by the robot
            #################################
            ############# AJAY ##############
            #################################
            with multiprocessing.Pool(processes=4) as pool:
                results_mat = pool.starmap(eng.is_reachable_mat, actions_list)

            for i in range(len(results_mat)):

                ## if the action can be successfully executed then update the current state 
                #################################
                ############# AJAY ##############
                #################################
                # if results_mat[i]['success'] == True:
                if results_mat[i] == True:

                    # include the action into the refined plan
                    new_actions.append(actions[i])

                    # ## make a ground action and apply it to the current state
                    # grounded_action = domain.ground(actions[i])
                    # state = state.apply(grounded_action)
                    # # if action.name in policy.prob_actions:
                    # #     print(bg_beige(action.__str__(body = True)))
                    # #     print(outcomes)
                    # # state = state.apply(action)

                    ## print out some info
                    # if args.verbose: 
                    print(fg_yellow('+'), actions[i].__str__(body = True))

                    # exit(1)

                ## if there is some failure
                else:

                    ## break the action into its name and args
                    action_name = actions_list[i][0]
                    action_args = actions_list[i][1]

                    ## if arm cannot reach the object (without any obstacle)
                    ## then remove ('arm_canreach', 'robot', 'object') from the current state
                    #################################
                    ############# AJAY ##############
                    #################################
                    # if action_args[0] cannot reach action_args[1]:
                    # if results_mat[i]['no_block']:
                    if False:


                        ## convert back the predicates frozenset to a list and update the state
                        ## i.e., remove ('arm_canreach', 'robot', 'object')
                        ## better to report the blocking objects by Ajay, i.e., 'robot' and 
                        ## 'object' should be identified by 'results_mat'
                        state_predicates = list(state.predicates)
                        state_predicates.remove(('arm_canreach', action_args[0], action_args[1]))
                        state.predicates = frozenset(state_predicates)

                        ## print out some info
                        # if args.verbose: 
                        print(fg_red('-'), action)
                        print(fg_red('@ arm', action_args[0], 'cannot reach', action_args[1]))

                    ## if there is an object blocking the target object
                    else:

                        ## return the obstructing objects
                        ## CURRENTLY WE ASSUME ONLY ONE OBJECT BLOCKS THE TARGET OBJECT!
                        #################################
                        ############# AJAY ##############
                        #################################
                        blocking_object = results_mat['obs_blocking']

                        ## convert back the predicates frozenset to a list and update the state
                        ## i.e., remove ('clear', 'object') and add ('blocked', 'object', 'blocking_object')
                        state_predicates = list(state.predicates)
                        state_predicates.remove(('clear', action_args[1]))
                        state_predicates.append(('blocked', action_args[1], objects_ref[blocking_object]))
                        state.predicates = frozenset(state_predicates)

                        ## print out some info
                        # if args.verbose: 
                        print(fg_red('-'), action)
                        print(fg_red('@', action_args[1], 'is blocked by', objects_ref[blocking_object]))

                    ## in either case break the for loop and make a replanning at the current updated state
                    ## note: the following three lines make sure to break from both (action and step) for-loops
                    break
            else:
                ## continue if the action is successfully executed (the inner for-loop wasn't broken)
                continue
            ## inner loop was broken, break the outer too (either reach or blocking failure happened)
            break



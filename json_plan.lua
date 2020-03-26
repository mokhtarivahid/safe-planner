-- loads a json file containing a plan into a plan table

colors = require 'ansicolors'
json = require "json"

-------- PRINT USAGE  -----------------------------
local function print_usage(arg)
    print('\nusage: lua json_plan.lua <JSON_PLAN_FILE> [-v] [-h]')
    print('\npositional arguments')
    print('  JSON_PLAN_FILE\tpath to the json plan file')
    print('\noptional arguments')
    print('  -h, --help\t\tshow this help message and exit')
    print('  -v, --verbose\t\tincrease verbosity (default=off)')
    os.exit()
end

-------- PARSE ARGS -------------------------------
local function parse_args(arg)
    file = ''
    verbose = false
    for key,value in ipairs(arg) do
        if value == '-v' or value == '--verbose' then
            verbose = true
        elseif value == '-h' or value == '--help' then
            print_usage(arg)
        else
            file = arg[1]
        end
    end
    return file, verbose
end

---------------------------------------------------
-- GLENN HAS TO DEVELOP THIS FUNCTION
---------------------------------------------------
-------- EXECUTE AN ACTION ------------------------
local function execute(step)
    -- this is a sample code to run a step and return its result

    -- unfold action and execute it
    for key, action in pairs(step.actions) do
        -- here the eTaSl has to be called to execute 'action'
        print(colors.yellow .. '\n' .. action .. colors.reset)
    end

    -- here you have to collect the action execution results
    -- together with human-intension estimation and return
    -- an outcome depending on the result
    -- the outcome is either successfully action executed or
    -- a human intention interference


    -- ignore this, it is a dummy code to simulate the outcome
    -- randomly generate an outcome
    math.randomseed(os.time())
    n = math.random(1, #step.outcomes)

    -- unfold outcome conditions
    for key, cnd in pairs(step.outcomes[n].condition) do
        print('    -- ' .. cnd)
    end

    return step.outcomes[n]
end


-------- MAIN -------------------------------------
-- parse args
local json_file, verbose = parse_args(arg)

-- open the json plan file
local file = io.open(json_file, "r")

-- load the json plan into a table
local table
if file then
    table = json.decode(file:read("*all"))
    file:close()
end

-- print out the json plan file
if verbose then
    pretty = require 'pl.pretty'
    pretty.dump(table)
end

-- the main loop to execute the plan
print(colors.green .. '\n[EXECUTION STARTS]' .. colors.reset)
-- start from the root
local step = 'step0'

while true do
    -- if there is no actions terminate the loop
    if table[step] == nil then
        print(colors.green .. '\n[TASK ACHIEVED]\n' .. colors.reset)
        break
    end

    -- execute actions and continue for the next action
    step = execute(table[step]).next

end


-- this file tests the generation of a dot graph from a json string
-- it uses the plan_translation module
json = require "json"

colors = require 'ansicolors'

-- graphviz:  to install type
-- sudo luarocks install graphviz (https://github.com/nymphium/lua-graphviz)
Graphviz = require("graphviz")
graph = Graphviz()

-- find the current directory
local curdir = debug.getinfo(1).source:match("^@(.-)([^\\/]-%.([^\\/%.]-))%.?$")
if string.len(curdir) > 0 then
    pt=require(curdir.."plan_translation")
else
    pt=require("plan_translation")
end

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

-------- MAIN -------------------------------------
-- parse args
local json_file, verbose = parse_args(arg)

-- open the json plan file
local file = io.open(json_file, "r")

-- load the json plan into a table
local table
if file then
    plan = json.decode(file:read("*all"))
    file:close()
end

-- print out the json plan file
if verbose then
    pretty = require 'pl.pretty'
    pretty.dump(plan)
end

--generate graph
graph = Graphviz()
pt.gen_graph(plan,"main",graph) 

--visualise
--graph:render("test.pdf")
graph:write(json_file ..".dot") -- use xdot to visualise the file


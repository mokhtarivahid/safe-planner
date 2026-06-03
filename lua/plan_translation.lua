-- this lua module contains the funcionalities to generate a dot graph and state machines given a totaluence of tasks
-- it uses the lua-graphviz library 
-- to install: sudo luarocks install graphviz (https://github.com/nymphium/lua-graphviz)
-- will use umf and fsm

local plan_translation = { _version = "0.1.0" }

local function has_value (tab, val)
	for key, value in ipairs(tab) do
		if value == val then
			return true
		end
	end
	return false
end

function plan_translation.gen_graph(plan,s_name,graph) -- plan structure, a string, the graph structure
	--if node
	if has_value(plan.actions,s_name) then
		graph:node(tostring(s_name), s_name)
		graph.nodes.style:update({style="filled",fillcolor="orange"})
		
		-- print ('node ' .. s_name)
		return s_name
	end
	if null==plan[s_name] then
		print ("ERROR " .. s_name) 
		return
	end
	graph.subgraphs['cluster_' .. s_name]=Graphviz()
	graph.subgraphs['cluster_' .. s_name].graph.style:update({label=s_name})
	
	if plan[s_name].ordering=='total' then
		--  print('cluster_' .. s_name .. " :total") 
		--graph.subgraphs['cluster_' .. s_name].graph.style:update({style="filled",color="\".7 .3 1.0\""})
		graph.subgraphs['cluster_' .. s_name].graph.style:update({color="black",fillcolor="white"})
		local names={}
		for key, value in ipairs(plan[s_name].list) do
			--  print ("call ".. key .. " plan_translation.gen_graph on " .. value .. "  " ..  'cluster_' .. s_name ) 
			local new_name=plan_translation.gen_graph(plan,value,graph.subgraphs['cluster_' .. s_name])
			if new_name==null then
				print ("error in calling cluster " .. 'cluster_' .. s_name.. " :total")
				for i,v in pairs (names) do print ("values" .. i,v) end
			else 
				table.insert(names,new_name);
			end
		end
		
		--add edges
		for i=1, #names -1 do
			start_points=plan_translation.find_the_start(plan,names[i+1])
			end_points=plan_translation.find_the_end(plan,names[i])
			if start_points~=null and end_points~=null then
				for isr,vsr in ipairs(start_points) do
					for isp,vsp in ipairs(end_points) do
						graph:edge(vsp, vsr)
					end
				end
			end
		end

		return ( s_name)
		
	elseif plan[s_name].ordering=='partial' then
		-- print('cluster_' .. s_name .. " :partial")
		graph.subgraphs['cluster_' .. s_name].graph.style:update({style="filled",fillcolor="grey"})
		for key, value in ipairs(plan[s_name].list) do
			local new_name=plan_translation.gen_graph(plan,value,graph.subgraphs['cluster_' .. s_name])
			if new_name==null then
				print ("error in calling cluster " .. 'cluster_' .. s_name .. " :partial")
			end
		end
		return ( s_name)

	elseif plan[s_name].ordering=='mutex' then
		-- print('cluster_' .. s_name .. " :mutex")
		graph.subgraphs['cluster_' .. s_name].graph.style:update({style="filled",fillcolor="dimgray"})
		for key, value in ipairs(plan[s_name].list) do
			local new_name=plan_translation.gen_graph(plan,value,graph.subgraphs['cluster_' .. s_name])
			if new_name==null then
				print ("error in calling cluster " .. 'cluster_' .. s_name .. " :mutex")
			end
		end
		return ( s_name)

	elseif plan[s_name].ordering=='concurrent' then
		-- print('cluster_' .. s_name .. " :concurrent")
		graph.subgraphs['cluster_' .. s_name].graph.style:update({style="filled",fillcolor="dimgray"})
		for key, value in ipairs(plan[s_name].list) do
			local new_name=plan_translation.gen_graph(plan,value,graph.subgraphs['cluster_' .. s_name])
			if new_name==null then
				print ("error in calling cluster " .. 'cluster_' .. s_name .. " :concurrent")
			end
		end
		return ( s_name)
	end

	print('ERROR ' .. s_name)
end


local function flatten(arr)
	local result = { }
	
	local function int_flatten(arr)
		for _, v in ipairs(arr) do
			if type(v) == "table" then
				int_flatten(v)
			else
				table.insert(result, v)
			end
		end
	end
	
	int_flatten(arr)
	return result
end


function plan_translation.find_the_start(plan,s_name)
	if has_value(plan.actions,s_name) then
		return {s_name}
	end
	local ret={}
	if null==plan[s_name] then
		print ("ERROR START " .. s_name) 
		return
	end
	if plan[s_name].ordering=='total' then
		ret=plan_translation.find_the_start(plan,plan[s_name].list[1])
	elseif plan[s_name].ordering=='partial' or plan[s_name].ordering=='mutex' or plan[s_name].ordering=='concurrent' then
		for i,v in ipairs (plan[s_name].list) do
			table.insert(ret, plan_translation.find_the_start(plan,v))
		end
		-- convert to single to list
	else
		print("ERROR FINALE START") 
		return
	end
	return flatten(ret)
end






function plan_translation.find_the_end(plan,s_name)
	if has_value(plan.actions,s_name) then
		return {s_name}
	end
	local ret={}
	if null==plan[s_name] then
		print ("ERROR END" .. s_name) 
		return
	end
	if plan[s_name].ordering=='total' then
		ret=plan_translation.find_the_end(plan,plan[s_name].list[#plan[s_name].list])
	elseif plan[s_name].ordering=='partial' or plan[s_name].ordering=='mutex' or plan[s_name].ordering=='concurrent' then
		for i,v in ipairs (plan[s_name].list) do
			--print("con  " .. v)
			table.insert(ret, plan_translation.find_the_end(plan,v))
		end
		-- convert to single to list
	else
		print("ERROR FINALE END") 
		return
	end
	return flatten(ret)
end



return plan_translation
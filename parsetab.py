
# parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'ACTION_KEY AND_KEY DEFINE_KEY DOMAIN_KEY EFFECT_KEY EQUALITY_KEY EQUALS GOAL_KEY HYPHEN INIT_KEY LPAREN NAME NOT_KEY OBJECTS_KEY PARAMETERS_KEY PRECONDITION_KEY PREDICATES_KEY PROBABILISTIC_EFFECTS_KEY PROBABILISTIC_KEY PROBABILITY PROBLEM_KEY REQUIREMENTS_KEY RPAREN STRIPS_KEY TYPES_KEY TYPING_KEY VARIABLE WHEN_KEYpddl : domain\n            | problemdomain : LPAREN DEFINE_KEY domain_def require_def types_def predicates_def action_def_lst RPAREN\n              | LPAREN DEFINE_KEY domain_def require_def predicates_def action_def_lst RPARENproblem : LPAREN DEFINE_KEY problem_def domain_def objects_def init_def goal_def RPAREN\n               | LPAREN DEFINE_KEY problem_def domain_def init_def goal_def RPARENdomain_def : LPAREN DOMAIN_KEY NAME RPARENproblem_def : LPAREN PROBLEM_KEY NAME RPARENobjects_def : LPAREN OBJECTS_KEY typed_constants_lst RPARENinit_def : LPAREN INIT_KEY LPAREN AND_KEY ground_predicates_lst RPAREN RPAREN\n                | LPAREN INIT_KEY ground_predicates_lst RPARENgoal_def : LPAREN GOAL_KEY LPAREN AND_KEY ground_predicates_lst RPAREN RPAREN\n                | LPAREN GOAL_KEY ground_predicates_lst RPARENrequire_def : LPAREN REQUIREMENTS_KEY require_key_lst RPARENrequire_key_lst : require_key require_key_lst\n                       | require_keyrequire_key : STRIPS_KEY\n                   | EQUALITY_KEY\n                   | TYPING_KEY\n                   | PROBABILISTIC_EFFECTS_KEYtypes_def : LPAREN TYPES_KEY names_lst RPARENpredicates_def : LPAREN PREDICATES_KEY predicate_def_lst RPARENpredicate_def_lst : predicate_def predicate_def_lst\n                         | predicate_defpredicate_def : LPAREN NAME typed_variables_lst RPAREN\n                     | LPAREN NAME RPARENaction_def_lst : action_def action_def_lst\n                      | action_defaction_def : LPAREN ACTION_KEY NAME parameters_def action_def_body RPARENparameters_def : PARAMETERS_KEY LPAREN typed_variables_lst RPAREN\n                      | PARAMETERS_KEY LPAREN RPARENaction_def_body : precond_def effects_defprecond_def : PRECONDITION_KEY LPAREN AND_KEY literals_lst RPAREN\n                   | PRECONDITION_KEY literaleffects_def : EFFECT_KEY LPAREN AND_KEY effects_lst RPAREN\n                   | EFFECT_KEY effecteffects_lst : effect effects_lst\n                   | effecteffect : literal\n              | LPAREN PROBABILISTIC_KEY PROBABILITY literal RPARENliterals_lst : literal literals_lst\n                    | literalliteral : LPAREN NOT_KEY predicate RPAREN\n               | predicateground_predicates_lst : ground_predicate ground_predicates_lst\n                             | ground_predicatepredicate : LPAREN NAME variables_lst RPAREN\n                 | LPAREN EQUALS VARIABLE VARIABLE RPAREN\n                 | LPAREN NAME RPARENground_predicate : LPAREN NAME constants_lst RPAREN\n                        | LPAREN NAME RPARENtyped_constants_lst : constants_lst HYPHEN type typed_constants_lst\n                           | constants_lst HYPHEN typetyped_variables_lst : variables_lst HYPHEN type typed_variables_lst\n                           | variables_lst HYPHEN typeconstants_lst : constant constants_lst\n                     | constantvariables_lst : VARIABLE variables_lst\n                     | VARIABLEnames_lst : NAME names_lst\n                 | NAMEtype : NAMEconstant : NAME'
    
_lr_action_items = {'DEFINE_KEY':([3,],[5,]),'OBJECTS_KEY':([17,],[28,]),'PROBABILISTIC_KEY':([120,141,],[129,129,]),'RPAREN':([18,19,25,32,33,34,35,36,37,40,42,47,48,50,51,52,54,55,57,58,61,62,64,65,67,69,73,74,80,81,83,85,86,87,88,89,90,93,94,95,97,98,99,100,101,104,105,106,108,110,111,115,117,118,119,121,122,124,128,132,133,134,136,138,140,142,143,144,145,147,148,149,150,151,152,],[30,31,46,-19,-16,56,-18,-17,-20,-28,60,68,-57,-63,71,-46,76,-15,77,-27,79,-61,82,-24,85,-56,-45,88,-60,93,-23,-13,-53,-62,-51,99,100,-26,-59,106,108,-52,-50,109,110,116,-58,-25,119,-29,-32,-44,127,-55,-12,-36,-39,133,-54,143,-49,144,146,-42,149,-38,-43,-47,151,-41,152,-35,-37,-48,-40,]),'REQUIREMENTS_KEY':([13,],[20,]),'$end':([1,2,4,46,60,68,77,],[0,-1,-2,-6,-4,-5,-3,]),'PROBABILISTIC_EFFECTS_KEY':([20,32,33,35,36,37,],[37,-19,37,-18,-17,-20,]),'LPAREN':([0,5,6,8,10,14,15,16,21,22,27,29,30,31,39,40,44,45,52,56,65,71,75,76,79,82,84,88,92,93,99,103,106,109,110,112,115,122,123,126,130,133,138,139,142,143,144,151,152,],[3,7,9,13,17,23,24,26,38,41,24,53,-7,-8,41,41,63,66,72,-14,63,-9,72,-11,-21,-22,72,-51,104,-26,-50,113,-25,-10,-29,120,-44,-39,131,137,141,-49,137,137,141,-43,-47,-48,-40,]),'PROBLEM_KEY':([7,],[12,]),'EQUALITY_KEY':([20,32,33,35,36,37,],[35,-19,35,-18,-17,-20,]),'HYPHEN':([48,49,50,69,94,96,105,],[-57,70,-63,-56,-59,107,-58,]),'PRECONDITION_KEY':([91,116,127,],[103,-31,-30,]),'VARIABLE':([81,87,94,104,118,124,125,135,],[94,-62,94,94,94,94,135,145,]),'GOAL_KEY':([24,],[45,]),'PROBABILITY':([129,],[139,]),'EQUALS':([113,120,131,137,141,],[125,125,125,125,125,]),'TYPES_KEY':([23,],[43,]),'PREDICATES_KEY':([23,38,],[44,44,]),'INIT_KEY':([17,26,],[29,29,]),'NAME':([11,12,28,43,48,50,53,59,62,63,66,70,72,74,86,87,107,113,120,131,137,141,],[18,19,50,62,50,-63,74,78,62,81,74,87,74,50,50,-62,87,124,124,124,124,124,]),'NOT_KEY':([113,120,137,141,],[123,123,123,123,]),'TYPING_KEY':([20,32,33,35,36,37,],[32,-19,32,-18,-17,-20,]),'PARAMETERS_KEY':([78,],[92,]),'STRIPS_KEY':([20,32,33,35,36,37,],[36,-19,36,-18,-17,-20,]),'EFFECT_KEY':([102,114,115,133,143,144,146,151,],[112,-34,-44,-49,-43,-47,-33,-48,]),'ACTION_KEY':([41,],[59,]),'DOMAIN_KEY':([7,9,],[11,11,]),'AND_KEY':([53,66,113,120,],[75,84,126,130,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'effects_def':([102,],[111,]),'typed_variables_lst':([81,104,118,],[95,117,128,]),'domain':([0,],[2,]),'init_def':([10,16,],[15,27,]),'parameters_def':([78,],[91,]),'require_def':([8,],[14,]),'problem_def':([5,],[6,]),'precond_def':([91,],[102,]),'constant':([28,48,74,86,],[48,48,48,48,]),'variables_lst':([81,94,104,118,124,],[96,105,96,96,134,]),'action_def_body':([91,],[101,]),'predicates_def':([14,21,],[22,39,]),'action_def_lst':([22,39,40,],[42,57,58,]),'type':([70,107,],[86,118,]),'require_key_lst':([20,33,],[34,55,]),'predicate':([103,112,123,126,130,138,139,142,],[115,115,132,115,115,115,115,115,]),'predicate_def':([44,65,],[65,65,]),'effects_lst':([130,142,],[140,150,]),'pddl':([0,],[1,]),'require_key':([20,33,],[33,33,]),'problem':([0,],[4,]),'action_def':([22,39,40,],[40,40,40,]),'names_lst':([43,62,],[61,80,]),'predicate_def_lst':([44,65,],[64,83,]),'typed_constants_lst':([28,86,],[51,98,]),'objects_def':([10,],[16,]),'ground_predicate':([29,45,52,75,84,],[52,52,52,52,52,]),'constants_lst':([28,48,74,86,],[49,69,89,49,]),'types_def':([14,],[21,]),'effect':([112,130,142,],[121,142,142,]),'literal':([103,112,126,130,138,139,142,],[114,122,138,122,138,148,122,]),'ground_predicates_lst':([29,45,52,75,84,],[54,67,73,90,97,]),'literals_lst':([126,138,],[136,147,]),'domain_def':([5,6,],[8,10,]),'goal_def':([15,27,],[25,47,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> pddl","S'",1,None,None,None),
  ('pddl -> domain','pddl',1,'p_pddl','pddlparser.py',128),
  ('pddl -> problem','pddl',1,'p_pddl','pddlparser.py',129),
  ('domain -> LPAREN DEFINE_KEY domain_def require_def types_def predicates_def action_def_lst RPAREN','domain',8,'p_domain','pddlparser.py',134),
  ('domain -> LPAREN DEFINE_KEY domain_def require_def predicates_def action_def_lst RPAREN','domain',7,'p_domain','pddlparser.py',135),
  ('problem -> LPAREN DEFINE_KEY problem_def domain_def objects_def init_def goal_def RPAREN','problem',8,'p_problem','pddlparser.py',143),
  ('problem -> LPAREN DEFINE_KEY problem_def domain_def init_def goal_def RPAREN','problem',7,'p_problem','pddlparser.py',144),
  ('domain_def -> LPAREN DOMAIN_KEY NAME RPAREN','domain_def',4,'p_domain_def','pddlparser.py',152),
  ('problem_def -> LPAREN PROBLEM_KEY NAME RPAREN','problem_def',4,'p_problem_def','pddlparser.py',157),
  ('objects_def -> LPAREN OBJECTS_KEY typed_constants_lst RPAREN','objects_def',4,'p_objects_def','pddlparser.py',162),
  ('init_def -> LPAREN INIT_KEY LPAREN AND_KEY ground_predicates_lst RPAREN RPAREN','init_def',7,'p_init_def','pddlparser.py',168),
  ('init_def -> LPAREN INIT_KEY ground_predicates_lst RPAREN','init_def',4,'p_init_def','pddlparser.py',169),
  ('goal_def -> LPAREN GOAL_KEY LPAREN AND_KEY ground_predicates_lst RPAREN RPAREN','goal_def',7,'p_goal_def','pddlparser.py',177),
  ('goal_def -> LPAREN GOAL_KEY ground_predicates_lst RPAREN','goal_def',4,'p_goal_def','pddlparser.py',178),
  ('require_def -> LPAREN REQUIREMENTS_KEY require_key_lst RPAREN','require_def',4,'p_require_def','pddlparser.py',186),
  ('require_key_lst -> require_key require_key_lst','require_key_lst',2,'p_require_key_lst','pddlparser.py',191),
  ('require_key_lst -> require_key','require_key_lst',1,'p_require_key_lst','pddlparser.py',192),
  ('require_key -> STRIPS_KEY','require_key',1,'p_require_key','pddlparser.py',200),
  ('require_key -> EQUALITY_KEY','require_key',1,'p_require_key','pddlparser.py',201),
  ('require_key -> TYPING_KEY','require_key',1,'p_require_key','pddlparser.py',202),
  ('require_key -> PROBABILISTIC_EFFECTS_KEY','require_key',1,'p_require_key','pddlparser.py',203),
  ('types_def -> LPAREN TYPES_KEY names_lst RPAREN','types_def',4,'p_types_def','pddlparser.py',208),
  ('predicates_def -> LPAREN PREDICATES_KEY predicate_def_lst RPAREN','predicates_def',4,'p_predicates_def','pddlparser.py',213),
  ('predicate_def_lst -> predicate_def predicate_def_lst','predicate_def_lst',2,'p_predicate_def_lst','pddlparser.py',218),
  ('predicate_def_lst -> predicate_def','predicate_def_lst',1,'p_predicate_def_lst','pddlparser.py',219),
  ('predicate_def -> LPAREN NAME typed_variables_lst RPAREN','predicate_def',4,'p_predicate_def','pddlparser.py',227),
  ('predicate_def -> LPAREN NAME RPAREN','predicate_def',3,'p_predicate_def','pddlparser.py',228),
  ('action_def_lst -> action_def action_def_lst','action_def_lst',2,'p_action_def_lst','pddlparser.py',236),
  ('action_def_lst -> action_def','action_def_lst',1,'p_action_def_lst','pddlparser.py',237),
  ('action_def -> LPAREN ACTION_KEY NAME parameters_def action_def_body RPAREN','action_def',6,'p_action_def','pddlparser.py',245),
  ('parameters_def -> PARAMETERS_KEY LPAREN typed_variables_lst RPAREN','parameters_def',4,'p_parameters_def','pddlparser.py',250),
  ('parameters_def -> PARAMETERS_KEY LPAREN RPAREN','parameters_def',3,'p_parameters_def','pddlparser.py',251),
  ('action_def_body -> precond_def effects_def','action_def_body',2,'p_action_def_body','pddlparser.py',259),
  ('precond_def -> PRECONDITION_KEY LPAREN AND_KEY literals_lst RPAREN','precond_def',5,'p_precond_def','pddlparser.py',264),
  ('precond_def -> PRECONDITION_KEY literal','precond_def',2,'p_precond_def','pddlparser.py',265),
  ('effects_def -> EFFECT_KEY LPAREN AND_KEY effects_lst RPAREN','effects_def',5,'p_effects_def','pddlparser.py',273),
  ('effects_def -> EFFECT_KEY effect','effects_def',2,'p_effects_def','pddlparser.py',274),
  ('effects_lst -> effect effects_lst','effects_lst',2,'p_effects_lst','pddlparser.py',282),
  ('effects_lst -> effect','effects_lst',1,'p_effects_lst','pddlparser.py',283),
  ('effect -> literal','effect',1,'p_effect','pddlparser.py',291),
  ('effect -> LPAREN PROBABILISTIC_KEY PROBABILITY literal RPAREN','effect',5,'p_effect','pddlparser.py',292),
  ('literals_lst -> literal literals_lst','literals_lst',2,'p_literals_lst','pddlparser.py',302),
  ('literals_lst -> literal','literals_lst',1,'p_literals_lst','pddlparser.py',303),
  ('literal -> LPAREN NOT_KEY predicate RPAREN','literal',4,'p_literal','pddlparser.py',311),
  ('literal -> predicate','literal',1,'p_literal','pddlparser.py',312),
  ('ground_predicates_lst -> ground_predicate ground_predicates_lst','ground_predicates_lst',2,'p_ground_predicates_lst','pddlparser.py',320),
  ('ground_predicates_lst -> ground_predicate','ground_predicates_lst',1,'p_ground_predicates_lst','pddlparser.py',321),
  ('predicate -> LPAREN NAME variables_lst RPAREN','predicate',4,'p_predicate','pddlparser.py',329),
  ('predicate -> LPAREN EQUALS VARIABLE VARIABLE RPAREN','predicate',5,'p_predicate','pddlparser.py',330),
  ('predicate -> LPAREN NAME RPAREN','predicate',3,'p_predicate','pddlparser.py',331),
  ('ground_predicate -> LPAREN NAME constants_lst RPAREN','ground_predicate',4,'p_ground_predicate','pddlparser.py',341),
  ('ground_predicate -> LPAREN NAME RPAREN','ground_predicate',3,'p_ground_predicate','pddlparser.py',342),
  ('typed_constants_lst -> constants_lst HYPHEN type typed_constants_lst','typed_constants_lst',4,'p_typed_constants_lst','pddlparser.py',350),
  ('typed_constants_lst -> constants_lst HYPHEN type','typed_constants_lst',3,'p_typed_constants_lst','pddlparser.py',351),
  ('typed_variables_lst -> variables_lst HYPHEN type typed_variables_lst','typed_variables_lst',4,'p_typed_variables_lst','pddlparser.py',359),
  ('typed_variables_lst -> variables_lst HYPHEN type','typed_variables_lst',3,'p_typed_variables_lst','pddlparser.py',360),
  ('constants_lst -> constant constants_lst','constants_lst',2,'p_constants_lst','pddlparser.py',368),
  ('constants_lst -> constant','constants_lst',1,'p_constants_lst','pddlparser.py',369),
  ('variables_lst -> VARIABLE variables_lst','variables_lst',2,'p_variables_lst','pddlparser.py',377),
  ('variables_lst -> VARIABLE','variables_lst',1,'p_variables_lst','pddlparser.py',378),
  ('names_lst -> NAME names_lst','names_lst',2,'p_names_lst','pddlparser.py',386),
  ('names_lst -> NAME','names_lst',1,'p_names_lst','pddlparser.py',387),
  ('type -> NAME','type',1,'p_type','pddlparser.py',397),
  ('constant -> NAME','constant',1,'p_constant','pddlparser.py',402),
]

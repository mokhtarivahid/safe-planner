
# parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'ACTION_KEY ADL_KEY AND_KEY CONDITIONAL_EFFECTS_KEY CONSTANTS_KEY DEFINE_KEY DERIVED_KEY DERIVED_PREDICATES_KEY DISJUNCTIVE_PRECONDITIONS_KEY DOMAIN_KEY EFFECT_KEY EQUALITY_KEY EQUALS EXISTENTIAL_PRECONDITIONS_KEY EXISTS_KEY FORALL_KEY GOAL_KEY HYPHEN INIT_KEY LPAREN NAME NEGATIVE_PRECONDITIONS_KEY NON_DETERMINISTIC_KEY NOT_KEY OBJECTS_KEY ONEOF_KEY PARAMETERS_KEY PRECONDITION_KEY PREDICATES_KEY PROBABILISTIC_EFFECTS_KEY PROBABILISTIC_KEY PROBABILITY PROBLEM_KEY REQUIREMENTS_KEY RPAREN STRIPS_KEY TYPES_KEY TYPING_KEY UNIVERSAL_PRECONDITIONS_KEY VARIABLE WHEN_KEYpddl : domain\n            | problem\n            | domain problemdomain : LPAREN DEFINE_KEY domain_structure_def_lst RPARENdomain_structure_def_lst : domain_structure_def domain_structure_def_lst\n                         | domain_structure_defdomain_structure_def : domain_def\n                     | require_def \n                     | types_def \n                     | constants_def \n                     | predicates_def\n                     | derived_predicates_def\n                     | action_def_lstdomain_def : LPAREN DOMAIN_KEY NAME RPARENrequire_def : LPAREN REQUIREMENTS_KEY require_key_lst RPARENrequire_key_lst : require_key require_key_lst\n                       | require_keyrequire_key : ADL_KEY\n                   | STRIPS_KEY\n                   | EQUALITY_KEY\n                   | TYPING_KEY\n                   | PROBABILISTIC_EFFECTS_KEY\n                   | NON_DETERMINISTIC_KEY\n                   | CONDITIONAL_EFFECTS_KEY\n                   | EXISTENTIAL_PRECONDITIONS_KEY\n                   | NEGATIVE_PRECONDITIONS_KEY\n                   | UNIVERSAL_PRECONDITIONS_KEY\n                   | DISJUNCTIVE_PRECONDITIONS_KEY\n                   | DERIVED_PREDICATES_KEYtypes_def : LPAREN TYPES_KEY typed_names_lst RPARENconstants_def : LPAREN CONSTANTS_KEY typed_constants_lst RPARENpredicates_def : LPAREN PREDICATES_KEY predicate_def_lst RPARENpredicate_def_lst : predicate_def predicate_def_lst\n                         | predicate_defpredicate_def : LPAREN NAME typed_variables_lst RPAREN\n                     | LPAREN NAME RPARENderived_predicates_def_lst : derived_predicates_def derived_predicates_def_lst\n                                  | derived_predicates_defderived_predicates_def :\n               | LPAREN DERIVED_KEY LPAREN NAME typed_variables_lst RPAREN precond RPAREN\n               | LPAREN DERIVED_KEY LPAREN NAME typed_variables_lst RPAREN LPAREN AND_KEY preconds_lst RPAREN RPAREN\n               | LPAREN DERIVED_KEY LPAREN NAME RPAREN precond RPAREN\n               | LPAREN DERIVED_KEY LPAREN NAME RPAREN LPAREN AND_KEY preconds_lst RPAREN RPARENaction_def_lst : action_def action_def_lst\n                      | action_defaction_def : LPAREN ACTION_KEY NAME action_def_body_list RPARENaction_def_body_list : action_def_body action_def_body_list\n                            | action_def_bodyaction_def_body : parameters_def\n                       | precond_def\n                       | effect_defparameters_def : PARAMETERS_KEY LPAREN typed_variables_lst RPAREN\n                      | PARAMETERS_KEY LPAREN RPARENprecond_def : PRECONDITION_KEY LPAREN AND_KEY preconds_lst RPAREN\n                   | PRECONDITION_KEY LPAREN RPAREN\n                   | PRECONDITION_KEY precondpreconds_lst : precond preconds_lst\n                    | precondprecond : literal\n               | universal_precond\n               | existential_preconduniversal_precond :\n               | LPAREN FORALL_KEY LPAREN typed_variables_lst RPAREN literal RPAREN\n               | LPAREN FORALL_KEY LPAREN typed_variables_lst RPAREN LPAREN AND_KEY literals_lst RPAREN RPARENexistential_precond :\n               | LPAREN EXISTS_KEY LPAREN typed_variables_lst RPAREN literal RPAREN\n               | LPAREN EXISTS_KEY LPAREN typed_variables_lst RPAREN LPAREN AND_KEY literals_lst RPAREN RPARENeffect_def : EFFECT_KEY LPAREN AND_KEY effect_lst RPAREN\n                  | EFFECT_KEY effecteffect_lst : effect effect_lst\n                  | effecteffect : literal\n              | conditional_for_eff\n              | conditional_when_eff\n              | LPAREN PROBABILISTIC_KEY prob_effect_lst RPAREN\n              | LPAREN ONEOF_KEY nd_effect_lst RPAREN\n              | LPAREN AND_KEY RPARENnd_effect_lst : nd_effect nd_effect_lst\n                     | nd_effectnd_effect : LPAREN AND_KEY effect_lst RPAREN\n                 | effectprob_effect_lst : prob_effect prob_effect_lst\n                       | prob_effectprob_effect : PROBABILITY LPAREN AND_KEY effect_lst RPAREN\n                   | PROBABILITY effectconditional_for_eff :\n               | LPAREN FORALL_KEY LPAREN typed_variables_lst RPAREN conditional_when_eff RPAREN\n               | LPAREN FORALL_KEY LPAREN typed_variables_lst RPAREN literal RPAREN\n               | LPAREN FORALL_KEY LPAREN typed_variables_lst RPAREN LPAREN AND_KEY literals_lst RPAREN RPARENconditional_when_eff :\n               | LPAREN WHEN_KEY literal literal RPAREN\n               | LPAREN WHEN_KEY LPAREN AND_KEY literals_lst RPAREN literal RPAREN\n               | LPAREN WHEN_KEY literal LPAREN AND_KEY literals_lst RPAREN RPAREN\n               | LPAREN WHEN_KEY LPAREN AND_KEY literals_lst RPAREN LPAREN AND_KEY literals_lst RPAREN RPAREN\n               literals_lst : literal literals_lst\n                    | literalliteral : LPAREN NOT_KEY predicate RPAREN\n               | predicateground_predicates_lst : ground_predicate ground_predicates_lst\n                             | ground_predicatepredicate : LPAREN NAME arguments_lst RPAREN\n                 | LPAREN EQUALS VARIABLE VARIABLE RPAREN\n                 | LPAREN EQUALS VARIABLE constant RPAREN\n                 | LPAREN EQUALS constant VARIABLE RPAREN\n                 | LPAREN NAME RPARENarguments_lst : constant arguments_lst\n                     | VARIABLE arguments_lst\n                     | constant\n                     | VARIABLEground_predicate : LPAREN NAME constants_lst RPAREN\n                        | LPAREN NAME RPARENtyped_constants_lst : constants_lst HYPHEN type typed_constants_lst\n                           | constants_lst HYPHEN typetyped_variables_lst : variables_lst HYPHEN type typed_variables_lst\n                           | variables_lst HYPHEN typeconstants_lst : constant constants_lst\n                     | constantvariables_lst : VARIABLE variables_lst\n                     | VARIABLEtyped_names_lst : names_lst HYPHEN type typed_names_lst\n                       | names_lst HYPHEN type\n                       | names_lstnames_lst : NAME names_lst\n                 | NAMEproblem : LPAREN DEFINE_KEY problem_structure_def_lst RPARENproblem_structure_def_lst : problem_structure_def problem_structure_def_lst\n                                 | problem_structure_defproblem_structure_def : problem_def\n                             | domain_def\n                             | objects_def\n                             | init_def\n                             | goal_defproblem_def : LPAREN PROBLEM_KEY NAME RPARENobjects_def : LPAREN OBJECTS_KEY typed_constants_lst RPARENinit_def : LPAREN INIT_KEY LPAREN AND_KEY ground_predicates_lst RPAREN RPAREN\n                | LPAREN INIT_KEY ground_predicates_lst RPARENgoal_def : LPAREN GOAL_KEY LPAREN AND_KEY ground_predicates_lst RPAREN RPAREN\n                | LPAREN GOAL_KEY ground_predicates_lst RPARENtype : NAMEconstant : NAME'
    
_lr_action_items = {'PROBABILITY':([111,113,115,116,138,163,165,166,179,199,201,209,211,215,228,229,230,233,256,257,258,269,270,278,282,],[-72,-74,-73,-98,165,165,-86,-77,-105,-75,-85,-97,-76,-101,-102,-103,-104,-91,-84,-87,-88,-93,-92,-89,-94,]),'ACTION_KEY':([12,27,44,],[29,29,29,]),'RPAREN':([5,8,9,10,11,13,14,15,16,17,18,19,20,21,22,23,24,26,40,41,43,45,48,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,68,70,71,72,74,75,77,78,79,80,81,82,83,85,86,87,88,89,90,92,94,95,96,97,98,99,101,102,104,105,106,107,108,110,111,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,132,133,134,135,136,137,139,143,144,146,147,149,151,152,153,154,156,159,160,161,162,163,164,165,166,168,169,173,175,176,178,179,180,181,182,185,188,189,191,192,193,194,196,197,198,199,201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,235,236,240,241,242,243,244,246,247,248,250,252,254,255,256,257,258,260,261,263,265,267,268,269,270,272,273,274,275,276,277,278,279,280,281,282,],[-39,-45,-130,-131,28,-128,-127,-8,-13,-132,-6,-9,-11,-12,46,-7,-10,-44,-129,-126,-7,-5,89,-100,94,95,-20,-22,-24,-18,-25,-27,-21,-28,96,-29,-23,-26,-17,-19,99,-117,-140,102,104,105,-34,-124,-122,110,-86,-51,-48,119,-49,-62,-50,-136,126,-99,-14,-133,-15,-16,128,-31,-116,-138,-134,-32,135,-33,-123,-30,-72,-74,-69,-73,-98,-47,146,-46,-59,-56,-60,-61,149,152,-111,153,-62,156,-113,-139,160,-36,161,-121,166,-86,179,-53,185,-55,-62,-110,191,192,-62,-112,197,-35,-120,-83,199,-86,-77,-71,204,209,-79,211,-81,-105,-109,-108,215,-52,221,-58,-135,-42,-62,224,-115,-137,-82,-75,-85,166,-70,-68,228,229,230,231,-97,-78,-76,166,-107,-106,-101,233,238,239,-54,-57,240,-40,-62,-114,166,-102,-103,-104,-90,246,-91,-96,249,254,255,256,257,258,-80,260,-95,263,265,-43,267,-84,-87,-88,269,270,-63,-66,-41,274,-93,-92,276,277,278,279,280,281,-89,282,-64,-67,-94,]),'EFFECT_KEY':([47,81,82,83,86,87,88,111,113,114,115,116,120,121,122,123,146,149,166,179,185,199,204,209,211,215,221,228,229,230,233,257,258,263,265,269,270,278,280,281,282,],[81,-86,-51,81,-49,-62,-50,-72,-74,-69,-73,-98,-59,-56,-60,-61,-53,-55,-77,-105,-52,-75,-68,-97,-76,-101,-54,-102,-103,-104,-91,-87,-88,-63,-66,-93,-92,-89,-64,-67,-94,]),'PROBABILISTIC_EFFECTS_KEY':([33,53,54,55,56,57,58,59,60,62,63,64,65,66,],[54,-20,-22,-24,-18,-25,-27,-21,-28,-29,-23,-26,54,-19,]),'$end':([1,2,4,6,28,46,],[-2,0,-1,-3,-125,-4,]),'WHEN_KEY':([112,167,177,200,245,],[145,145,145,145,145,]),'DEFINE_KEY':([3,7,],[5,25,]),'DOMAIN_KEY':([12,42,44,],[31,31,31,]),'PROBLEM_KEY':([12,42,],[32,32,]),'REQUIREMENTS_KEY':([12,44,],[33,33,]),'UNIVERSAL_PRECONDITIONS_KEY':([33,53,54,55,56,57,58,59,60,62,63,64,65,66,],[58,-20,-22,-24,-18,-25,-27,-21,-28,-29,-23,-26,58,-19,]),'PARAMETERS_KEY':([47,81,82,83,86,87,88,111,113,114,115,116,120,121,122,123,146,149,166,179,185,199,204,209,211,215,221,228,229,230,233,257,258,263,265,269,270,278,280,281,282,],[84,-86,-51,84,-49,-62,-50,-72,-74,-69,-73,-98,-59,-56,-60,-61,-53,-55,-77,-105,-52,-75,-68,-97,-76,-101,-54,-102,-103,-104,-91,-87,-88,-63,-66,-93,-92,-89,-64,-67,-94,]),'VARIABLE':([71,98,106,118,131,133,140,144,170,171,172,180,181,186,187,196,],[-140,131,131,131,131,-139,170,180,205,207,131,180,180,131,131,131,]),'TYPES_KEY':([12,44,],[39,39,]),'DERIVED_KEY':([12,44,],[34,34,]),'PROBABILISTIC_KEY':([112,167,177,200,],[138,138,138,138,]),'CONSTANTS_KEY':([12,44,],[35,35,]),'AND_KEY':([49,73,112,124,155,167,177,184,195,200,217,245,251,253,262,],[91,103,139,151,193,202,212,218,225,227,234,259,264,266,271,]),'LPAREN':([0,4,5,8,9,10,13,14,15,16,17,18,19,20,21,23,24,25,26,30,34,36,38,40,43,46,50,77,81,84,87,89,91,94,95,96,99,102,103,104,105,110,111,113,115,116,119,120,122,123,126,128,135,139,141,142,143,145,148,150,151,152,156,161,165,166,168,175,178,179,183,189,191,192,193,197,199,209,211,212,215,218,224,225,227,228,229,230,231,233,234,235,238,239,246,249,254,257,258,259,263,264,265,266,267,269,270,271,278,280,281,282,],[3,7,12,27,-130,-131,-128,42,-8,-13,-132,44,-9,-11,-12,-7,-10,42,-44,49,67,73,76,-129,-7,-4,93,76,112,118,124,-136,93,-14,-133,-15,-31,-138,93,-134,-32,-30,-72,-74,-73,-98,-46,-59,-60,-61,-111,155,-36,167,172,174,177,184,186,187,190,-110,195,-35,200,-77,167,177,-81,-105,217,190,-135,-42,190,-137,-75,-97,-76,167,-101,237,-40,190,167,-102,-103,-104,245,-91,237,237,251,253,-80,262,-43,-87,-88,237,-63,237,-66,237,-41,-93,-92,237,-89,-64,-67,-94,]),'EXISTENTIAL_PRECONDITIONS_KEY':([33,53,54,55,56,57,58,59,60,62,63,64,65,66,],[57,-20,-22,-24,-18,-25,-27,-21,-28,-29,-23,-26,57,-19,]),'DERIVED_PREDICATES_KEY':([33,53,54,55,56,57,58,59,60,62,63,64,65,66,],[62,-20,-22,-24,-18,-25,-27,-21,-28,-29,-23,-26,62,-19,]),'NAME':([29,31,32,35,37,39,49,67,70,71,73,76,78,90,93,100,109,112,124,132,133,137,140,144,155,157,167,170,174,177,180,181,184,190,195,200,217,237,245,251,253,262,],[47,51,52,71,71,78,90,98,71,-140,90,106,78,71,90,133,133,144,144,71,-139,78,71,71,144,133,144,71,144,144,71,71,144,144,144,144,144,144,144,144,144,144,]),'FORALL_KEY':([112,124,155,167,177,190,195,200,],[141,148,148,141,141,148,148,141,]),'NON_DETERMINISTIC_KEY':([33,53,54,55,56,57,58,59,60,62,63,64,65,66,],[63,-20,-22,-24,-18,-25,-27,-21,-28,-29,-23,-26,63,-19,]),'INIT_KEY':([12,42,],[30,30,]),'EQUALITY_KEY':([33,53,54,55,56,57,58,59,60,62,63,64,65,66,],[53,-20,-22,-24,-18,-25,-27,-21,-28,-29,-23,-26,53,-19,]),'NOT_KEY':([112,124,155,167,177,184,190,195,200,217,237,245,251,253,262,],[142,142,142,142,142,142,142,142,142,142,142,142,142,142,142,]),'EQUALS':([112,124,155,167,174,177,184,190,195,200,217,237,245,251,253,262,],[140,140,140,140,140,140,140,140,140,140,140,140,140,140,140,140,]),'CONDITIONAL_EFFECTS_KEY':([33,53,54,55,56,57,58,59,60,62,63,64,65,66,],[55,-20,-22,-24,-18,-25,-27,-21,-28,-29,-23,-26,55,-19,]),'ADL_KEY':([33,53,54,55,56,57,58,59,60,62,63,64,65,66,],[56,-20,-22,-24,-18,-25,-27,-21,-28,-29,-23,-26,56,-19,]),'HYPHEN':([69,70,71,78,79,101,108,130,131,158,],[100,-117,-140,-124,109,-116,-123,157,-119,-118,]),'GOAL_KEY':([12,42,],[36,36,]),'EXISTS_KEY':([124,155,190,195,],[150,150,150,150,]),'ONEOF_KEY':([112,167,177,200,],[143,143,143,143,]),'OBJECTS_KEY':([12,42,],[37,37,]),'PREDICATES_KEY':([12,44,],[38,38,]),'PRECONDITION_KEY':([47,81,82,83,86,87,88,111,113,114,115,116,120,121,122,123,146,149,166,179,185,199,204,209,211,215,221,228,229,230,233,257,258,263,265,269,270,278,280,281,282,],[87,-86,-51,87,-49,-62,-50,-72,-74,-69,-73,-98,-59,-56,-60,-61,-53,-55,-77,-105,-52,-75,-68,-97,-76,-101,-54,-102,-103,-104,-91,-87,-88,-63,-66,-93,-92,-89,-64,-67,-94,]),'DISJUNCTIVE_PRECONDITIONS_KEY':([33,53,54,55,56,57,58,59,60,62,63,64,65,66,],[60,-20,-22,-24,-18,-25,-27,-21,-28,-29,-23,-26,60,-19,]),'TYPING_KEY':([33,53,54,55,56,57,58,59,60,62,63,64,65,66,],[59,-20,-22,-24,-18,-25,-27,-21,-28,-29,-23,-26,59,-19,]),'NEGATIVE_PRECONDITIONS_KEY':([33,53,54,55,56,57,58,59,60,62,63,64,65,66,],[64,-20,-22,-24,-18,-25,-27,-21,-28,-29,-23,-26,64,-19,]),'STRIPS_KEY':([33,53,54,55,56,57,58,59,60,62,63,64,65,66,],[66,-20,-22,-24,-18,-25,-27,-21,-28,-29,-23,-26,66,-19,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'problem':([0,4,],[1,6,]),'action_def':([5,8,18,],[8,8,8,]),'domain_def':([5,14,18,25,],[23,40,43,40,]),'nd_effect':([143,175,],[175,175,]),'literals_lst':([218,234,235,259,264,266,271,],[236,247,248,268,272,273,275,]),'pddl':([0,],[2,]),'domain':([0,],[4,]),'typed_constants_lst':([35,37,132,],[68,74,159,]),'ground_predicates_lst':([30,36,50,91,103,],[48,72,92,127,134,]),'init_def':([5,14,25,],[10,10,10,]),'variables_lst':([98,106,118,131,172,186,187,196,],[130,130,130,158,130,130,130,130,]),'nd_effect_lst':([143,175,],[176,210,]),'require_key':([33,65,],[65,65,]),'problem_structure_def':([5,14,25,],[14,14,14,]),'conditional_when_eff':([81,139,143,165,168,175,212,227,231,],[113,113,113,113,113,113,113,113,243,]),'effect':([81,139,143,165,168,175,212,227,],[114,168,178,201,168,178,168,168,]),'require_def':([5,18,],[15,15,]),'predicates_def':([5,18,],[20,20,]),'types_def':([5,18,],[19,19,]),'ground_predicate':([30,36,50,91,103,],[50,50,50,50,50,]),'action_def_body':([47,83,],[83,83,]),'typed_variables_lst':([98,106,118,172,186,187,196,],[129,136,147,208,219,220,226,]),'action_def_body_list':([47,83,],[85,117,]),'existential_precond':([87,128,151,156,189,193,225,],[123,123,123,123,123,123,123,]),'derived_predicates_def':([5,18,],[21,21,]),'arguments_lst':([144,180,181,],[182,213,214,]),'type':([100,109,157,],[132,137,196,]),'predicate_def':([38,77,],[77,77,]),'constant':([35,37,70,90,132,140,144,170,180,181,],[70,70,70,70,70,171,181,206,181,181,]),'preconds_lst':([151,189,193,225,],[188,222,223,241,]),'literal':([81,87,128,139,143,145,151,156,165,168,175,183,189,193,212,218,225,227,231,234,235,238,239,249,259,264,266,271,],[111,120,120,111,111,183,120,120,111,111,111,216,120,120,111,235,120,111,244,235,235,250,252,261,235,235,235,235,]),'objects_def':([5,14,25,],[9,9,9,]),'typed_names_lst':([39,137,],[80,162,]),'universal_precond':([87,128,151,156,189,193,225,],[122,122,122,122,122,122,122,]),'problem_structure_def_lst':([5,14,25,],[11,41,11,]),'predicate_def_lst':([38,77,],[75,107,]),'require_key_lst':([33,65,],[61,97,]),'precond_def':([47,83,],[88,88,]),'parameters_def':([47,83,],[86,86,]),'conditional_for_eff':([81,139,143,165,168,175,212,227,],[115,115,115,115,115,115,115,115,]),'precond':([87,128,151,156,189,193,225,],[121,154,189,194,189,189,189,]),'problem_def':([5,14,25,],[13,13,13,]),'action_def_lst':([5,8,18,],[16,26,16,]),'prob_effect':([138,163,],[163,163,]),'goal_def':([5,14,25,],[17,17,17,]),'predicate':([81,87,128,139,142,143,145,151,156,165,168,175,183,189,193,212,218,225,227,231,234,235,238,239,249,259,264,266,271,],[116,116,116,116,173,116,116,116,116,116,116,116,116,116,116,116,116,116,116,116,116,116,116,116,116,116,116,116,116,]),'domain_structure_def':([5,18,],[18,18,]),'constants_def':([5,18,],[24,24,]),'effect_def':([47,83,],[82,82,]),'constants_lst':([35,37,70,90,132,],[69,69,101,125,69,]),'effect_lst':([139,168,212,227,],[169,203,232,242,]),'prob_effect_lst':([138,163,],[164,198,]),'domain_structure_def_lst':([5,18,],[22,45,]),'names_lst':([39,78,137,],[79,108,79,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> pddl","S'",1,None,None,None),
  ('pddl -> domain','pddl',1,'p_pddl','pddlparser.py',159),
  ('pddl -> problem','pddl',1,'p_pddl','pddlparser.py',160),
  ('pddl -> domain problem','pddl',2,'p_pddl','pddlparser.py',161),
  ('domain -> LPAREN DEFINE_KEY domain_structure_def_lst RPAREN','domain',4,'p_domain','pddlparser.py',169),
  ('domain_structure_def_lst -> domain_structure_def domain_structure_def_lst','domain_structure_def_lst',2,'p_domain_structure_def_lst','pddlparser.py',195),
  ('domain_structure_def_lst -> domain_structure_def','domain_structure_def_lst',1,'p_domain_structure_def_lst','pddlparser.py',196),
  ('domain_structure_def -> domain_def','domain_structure_def',1,'p_domain_structure_def','pddlparser.py',204),
  ('domain_structure_def -> require_def','domain_structure_def',1,'p_domain_structure_def','pddlparser.py',205),
  ('domain_structure_def -> types_def','domain_structure_def',1,'p_domain_structure_def','pddlparser.py',206),
  ('domain_structure_def -> constants_def','domain_structure_def',1,'p_domain_structure_def','pddlparser.py',207),
  ('domain_structure_def -> predicates_def','domain_structure_def',1,'p_domain_structure_def','pddlparser.py',208),
  ('domain_structure_def -> derived_predicates_def','domain_structure_def',1,'p_domain_structure_def','pddlparser.py',209),
  ('domain_structure_def -> action_def_lst','domain_structure_def',1,'p_domain_structure_def','pddlparser.py',210),
  ('domain_def -> LPAREN DOMAIN_KEY NAME RPAREN','domain_def',4,'p_domain_def','pddlparser.py',215),
  ('require_def -> LPAREN REQUIREMENTS_KEY require_key_lst RPAREN','require_def',4,'p_require_def','pddlparser.py',220),
  ('require_key_lst -> require_key require_key_lst','require_key_lst',2,'p_require_key_lst','pddlparser.py',225),
  ('require_key_lst -> require_key','require_key_lst',1,'p_require_key_lst','pddlparser.py',226),
  ('require_key -> ADL_KEY','require_key',1,'p_require_key','pddlparser.py',234),
  ('require_key -> STRIPS_KEY','require_key',1,'p_require_key','pddlparser.py',235),
  ('require_key -> EQUALITY_KEY','require_key',1,'p_require_key','pddlparser.py',236),
  ('require_key -> TYPING_KEY','require_key',1,'p_require_key','pddlparser.py',237),
  ('require_key -> PROBABILISTIC_EFFECTS_KEY','require_key',1,'p_require_key','pddlparser.py',238),
  ('require_key -> NON_DETERMINISTIC_KEY','require_key',1,'p_require_key','pddlparser.py',239),
  ('require_key -> CONDITIONAL_EFFECTS_KEY','require_key',1,'p_require_key','pddlparser.py',240),
  ('require_key -> EXISTENTIAL_PRECONDITIONS_KEY','require_key',1,'p_require_key','pddlparser.py',241),
  ('require_key -> NEGATIVE_PRECONDITIONS_KEY','require_key',1,'p_require_key','pddlparser.py',242),
  ('require_key -> UNIVERSAL_PRECONDITIONS_KEY','require_key',1,'p_require_key','pddlparser.py',243),
  ('require_key -> DISJUNCTIVE_PRECONDITIONS_KEY','require_key',1,'p_require_key','pddlparser.py',244),
  ('require_key -> DERIVED_PREDICATES_KEY','require_key',1,'p_require_key','pddlparser.py',245),
  ('types_def -> LPAREN TYPES_KEY typed_names_lst RPAREN','types_def',4,'p_types_def','pddlparser.py',250),
  ('constants_def -> LPAREN CONSTANTS_KEY typed_constants_lst RPAREN','constants_def',4,'p_constants_def','pddlparser.py',260),
  ('predicates_def -> LPAREN PREDICATES_KEY predicate_def_lst RPAREN','predicates_def',4,'p_predicates_def','pddlparser.py',270),
  ('predicate_def_lst -> predicate_def predicate_def_lst','predicate_def_lst',2,'p_predicate_def_lst','pddlparser.py',275),
  ('predicate_def_lst -> predicate_def','predicate_def_lst',1,'p_predicate_def_lst','pddlparser.py',276),
  ('predicate_def -> LPAREN NAME typed_variables_lst RPAREN','predicate_def',4,'p_predicate_def','pddlparser.py',284),
  ('predicate_def -> LPAREN NAME RPAREN','predicate_def',3,'p_predicate_def','pddlparser.py',285),
  ('derived_predicates_def_lst -> derived_predicates_def derived_predicates_def_lst','derived_predicates_def_lst',2,'p_derived_predicates_def_lst','pddlparser.py',294),
  ('derived_predicates_def_lst -> derived_predicates_def','derived_predicates_def_lst',1,'p_derived_predicates_def_lst','pddlparser.py',295),
  ('derived_predicates_def -> <empty>','derived_predicates_def',0,'p_derived_predicates_def','pddlparser.py',303),
  ('derived_predicates_def -> LPAREN DERIVED_KEY LPAREN NAME typed_variables_lst RPAREN precond RPAREN','derived_predicates_def',8,'p_derived_predicates_def','pddlparser.py',304),
  ('derived_predicates_def -> LPAREN DERIVED_KEY LPAREN NAME typed_variables_lst RPAREN LPAREN AND_KEY preconds_lst RPAREN RPAREN','derived_predicates_def',11,'p_derived_predicates_def','pddlparser.py',305),
  ('derived_predicates_def -> LPAREN DERIVED_KEY LPAREN NAME RPAREN precond RPAREN','derived_predicates_def',7,'p_derived_predicates_def','pddlparser.py',306),
  ('derived_predicates_def -> LPAREN DERIVED_KEY LPAREN NAME RPAREN LPAREN AND_KEY preconds_lst RPAREN RPAREN','derived_predicates_def',10,'p_derived_predicates_def','pddlparser.py',307),
  ('action_def_lst -> action_def action_def_lst','action_def_lst',2,'p_action_def_lst','pddlparser.py',330),
  ('action_def_lst -> action_def','action_def_lst',1,'p_action_def_lst','pddlparser.py',331),
  ('action_def -> LPAREN ACTION_KEY NAME action_def_body_list RPAREN','action_def',5,'p_action_def','pddlparser.py',339),
  ('action_def_body_list -> action_def_body action_def_body_list','action_def_body_list',2,'p_action_def_body_list','pddlparser.py',357),
  ('action_def_body_list -> action_def_body','action_def_body_list',1,'p_action_def_body_list','pddlparser.py',358),
  ('action_def_body -> parameters_def','action_def_body',1,'p_action_def_body','pddlparser.py',366),
  ('action_def_body -> precond_def','action_def_body',1,'p_action_def_body','pddlparser.py',367),
  ('action_def_body -> effect_def','action_def_body',1,'p_action_def_body','pddlparser.py',368),
  ('parameters_def -> PARAMETERS_KEY LPAREN typed_variables_lst RPAREN','parameters_def',4,'p_parameters_def','pddlparser.py',373),
  ('parameters_def -> PARAMETERS_KEY LPAREN RPAREN','parameters_def',3,'p_parameters_def','pddlparser.py',374),
  ('precond_def -> PRECONDITION_KEY LPAREN AND_KEY preconds_lst RPAREN','precond_def',5,'p_precond_def','pddlparser.py',382),
  ('precond_def -> PRECONDITION_KEY LPAREN RPAREN','precond_def',3,'p_precond_def','pddlparser.py',383),
  ('precond_def -> PRECONDITION_KEY precond','precond_def',2,'p_precond_def','pddlparser.py',384),
  ('preconds_lst -> precond preconds_lst','preconds_lst',2,'p_preconds_lst','pddlparser.py',405),
  ('preconds_lst -> precond','preconds_lst',1,'p_preconds_lst','pddlparser.py',406),
  ('precond -> literal','precond',1,'p_precond','pddlparser.py',414),
  ('precond -> universal_precond','precond',1,'p_precond','pddlparser.py',415),
  ('precond -> existential_precond','precond',1,'p_precond','pddlparser.py',416),
  ('universal_precond -> <empty>','universal_precond',0,'p_universal_precond','pddlparser.py',421),
  ('universal_precond -> LPAREN FORALL_KEY LPAREN typed_variables_lst RPAREN literal RPAREN','universal_precond',7,'p_universal_precond','pddlparser.py',422),
  ('universal_precond -> LPAREN FORALL_KEY LPAREN typed_variables_lst RPAREN LPAREN AND_KEY literals_lst RPAREN RPAREN','universal_precond',10,'p_universal_precond','pddlparser.py',423),
  ('existential_precond -> <empty>','existential_precond',0,'p_existential_precond','pddlparser.py',431),
  ('existential_precond -> LPAREN EXISTS_KEY LPAREN typed_variables_lst RPAREN literal RPAREN','existential_precond',7,'p_existential_precond','pddlparser.py',432),
  ('existential_precond -> LPAREN EXISTS_KEY LPAREN typed_variables_lst RPAREN LPAREN AND_KEY literals_lst RPAREN RPAREN','existential_precond',10,'p_existential_precond','pddlparser.py',433),
  ('effect_def -> EFFECT_KEY LPAREN AND_KEY effect_lst RPAREN','effect_def',5,'p_effect_def','pddlparser.py',441),
  ('effect_def -> EFFECT_KEY effect','effect_def',2,'p_effect_def','pddlparser.py',442),
  ('effect_lst -> effect effect_lst','effect_lst',2,'p_effect_lst','pddlparser.py',481),
  ('effect_lst -> effect','effect_lst',1,'p_effect_lst','pddlparser.py',482),
  ('effect -> literal','effect',1,'p_effect','pddlparser.py',490),
  ('effect -> conditional_for_eff','effect',1,'p_effect','pddlparser.py',491),
  ('effect -> conditional_when_eff','effect',1,'p_effect','pddlparser.py',492),
  ('effect -> LPAREN PROBABILISTIC_KEY prob_effect_lst RPAREN','effect',4,'p_effect','pddlparser.py',493),
  ('effect -> LPAREN ONEOF_KEY nd_effect_lst RPAREN','effect',4,'p_effect','pddlparser.py',494),
  ('effect -> LPAREN AND_KEY RPAREN','effect',3,'p_effect','pddlparser.py',495),
  ('nd_effect_lst -> nd_effect nd_effect_lst','nd_effect_lst',2,'p_nd_effect_lst','pddlparser.py',507),
  ('nd_effect_lst -> nd_effect','nd_effect_lst',1,'p_nd_effect_lst','pddlparser.py',508),
  ('nd_effect -> LPAREN AND_KEY effect_lst RPAREN','nd_effect',4,'p_nd_effect','pddlparser.py',516),
  ('nd_effect -> effect','nd_effect',1,'p_nd_effect','pddlparser.py',517),
  ('prob_effect_lst -> prob_effect prob_effect_lst','prob_effect_lst',2,'p_prob_effect_lst','pddlparser.py',525),
  ('prob_effect_lst -> prob_effect','prob_effect_lst',1,'p_prob_effect_lst','pddlparser.py',526),
  ('prob_effect -> PROBABILITY LPAREN AND_KEY effect_lst RPAREN','prob_effect',5,'p_prob_effect','pddlparser.py',534),
  ('prob_effect -> PROBABILITY effect','prob_effect',2,'p_prob_effect','pddlparser.py',535),
  ('conditional_for_eff -> <empty>','conditional_for_eff',0,'p_conditional_for_eff','pddlparser.py',543),
  ('conditional_for_eff -> LPAREN FORALL_KEY LPAREN typed_variables_lst RPAREN conditional_when_eff RPAREN','conditional_for_eff',7,'p_conditional_for_eff','pddlparser.py',544),
  ('conditional_for_eff -> LPAREN FORALL_KEY LPAREN typed_variables_lst RPAREN literal RPAREN','conditional_for_eff',7,'p_conditional_for_eff','pddlparser.py',545),
  ('conditional_for_eff -> LPAREN FORALL_KEY LPAREN typed_variables_lst RPAREN LPAREN AND_KEY literals_lst RPAREN RPAREN','conditional_for_eff',10,'p_conditional_for_eff','pddlparser.py',546),
  ('conditional_when_eff -> <empty>','conditional_when_eff',0,'p_conditional_when_eff','pddlparser.py',557),
  ('conditional_when_eff -> LPAREN WHEN_KEY literal literal RPAREN','conditional_when_eff',5,'p_conditional_when_eff','pddlparser.py',558),
  ('conditional_when_eff -> LPAREN WHEN_KEY LPAREN AND_KEY literals_lst RPAREN literal RPAREN','conditional_when_eff',8,'p_conditional_when_eff','pddlparser.py',559),
  ('conditional_when_eff -> LPAREN WHEN_KEY literal LPAREN AND_KEY literals_lst RPAREN RPAREN','conditional_when_eff',8,'p_conditional_when_eff','pddlparser.py',560),
  ('conditional_when_eff -> LPAREN WHEN_KEY LPAREN AND_KEY literals_lst RPAREN LPAREN AND_KEY literals_lst RPAREN RPAREN','conditional_when_eff',11,'p_conditional_when_eff','pddlparser.py',561),
  ('literals_lst -> literal literals_lst','literals_lst',2,'p_literals_lst','pddlparser.py',575),
  ('literals_lst -> literal','literals_lst',1,'p_literals_lst','pddlparser.py',576),
  ('literal -> LPAREN NOT_KEY predicate RPAREN','literal',4,'p_literal','pddlparser.py',584),
  ('literal -> predicate','literal',1,'p_literal','pddlparser.py',585),
  ('ground_predicates_lst -> ground_predicate ground_predicates_lst','ground_predicates_lst',2,'p_ground_predicates_lst','pddlparser.py',593),
  ('ground_predicates_lst -> ground_predicate','ground_predicates_lst',1,'p_ground_predicates_lst','pddlparser.py',594),
  ('predicate -> LPAREN NAME arguments_lst RPAREN','predicate',4,'p_predicate','pddlparser.py',602),
  ('predicate -> LPAREN EQUALS VARIABLE VARIABLE RPAREN','predicate',5,'p_predicate','pddlparser.py',603),
  ('predicate -> LPAREN EQUALS VARIABLE constant RPAREN','predicate',5,'p_predicate','pddlparser.py',604),
  ('predicate -> LPAREN EQUALS constant VARIABLE RPAREN','predicate',5,'p_predicate','pddlparser.py',605),
  ('predicate -> LPAREN NAME RPAREN','predicate',3,'p_predicate','pddlparser.py',606),
  ('arguments_lst -> constant arguments_lst','arguments_lst',2,'p_arguments_lst','pddlparser.py',616),
  ('arguments_lst -> VARIABLE arguments_lst','arguments_lst',2,'p_arguments_lst','pddlparser.py',617),
  ('arguments_lst -> constant','arguments_lst',1,'p_arguments_lst','pddlparser.py',618),
  ('arguments_lst -> VARIABLE','arguments_lst',1,'p_arguments_lst','pddlparser.py',619),
  ('ground_predicate -> LPAREN NAME constants_lst RPAREN','ground_predicate',4,'p_ground_predicate','pddlparser.py',627),
  ('ground_predicate -> LPAREN NAME RPAREN','ground_predicate',3,'p_ground_predicate','pddlparser.py',628),
  ('typed_constants_lst -> constants_lst HYPHEN type typed_constants_lst','typed_constants_lst',4,'p_typed_constants_lst','pddlparser.py',636),
  ('typed_constants_lst -> constants_lst HYPHEN type','typed_constants_lst',3,'p_typed_constants_lst','pddlparser.py',637),
  ('typed_variables_lst -> variables_lst HYPHEN type typed_variables_lst','typed_variables_lst',4,'p_typed_variables_lst','pddlparser.py',645),
  ('typed_variables_lst -> variables_lst HYPHEN type','typed_variables_lst',3,'p_typed_variables_lst','pddlparser.py',646),
  ('constants_lst -> constant constants_lst','constants_lst',2,'p_constants_lst','pddlparser.py',654),
  ('constants_lst -> constant','constants_lst',1,'p_constants_lst','pddlparser.py',655),
  ('variables_lst -> VARIABLE variables_lst','variables_lst',2,'p_variables_lst','pddlparser.py',663),
  ('variables_lst -> VARIABLE','variables_lst',1,'p_variables_lst','pddlparser.py',664),
  ('typed_names_lst -> names_lst HYPHEN type typed_names_lst','typed_names_lst',4,'p_typed_names_lst','pddlparser.py',672),
  ('typed_names_lst -> names_lst HYPHEN type','typed_names_lst',3,'p_typed_names_lst','pddlparser.py',673),
  ('typed_names_lst -> names_lst','typed_names_lst',1,'p_typed_names_lst','pddlparser.py',674),
  ('names_lst -> NAME names_lst','names_lst',2,'p_names_lst','pddlparser.py',684),
  ('names_lst -> NAME','names_lst',1,'p_names_lst','pddlparser.py',685),
  ('problem -> LPAREN DEFINE_KEY problem_structure_def_lst RPAREN','problem',4,'p_problem','pddlparser.py',695),
  ('problem_structure_def_lst -> problem_structure_def problem_structure_def_lst','problem_structure_def_lst',2,'p_problem_structure_def_lst','pddlparser.py',718),
  ('problem_structure_def_lst -> problem_structure_def','problem_structure_def_lst',1,'p_problem_structure_def_lst','pddlparser.py',719),
  ('problem_structure_def -> problem_def','problem_structure_def',1,'p_problem_structure_def','pddlparser.py',727),
  ('problem_structure_def -> domain_def','problem_structure_def',1,'p_problem_structure_def','pddlparser.py',728),
  ('problem_structure_def -> objects_def','problem_structure_def',1,'p_problem_structure_def','pddlparser.py',729),
  ('problem_structure_def -> init_def','problem_structure_def',1,'p_problem_structure_def','pddlparser.py',730),
  ('problem_structure_def -> goal_def','problem_structure_def',1,'p_problem_structure_def','pddlparser.py',731),
  ('problem_def -> LPAREN PROBLEM_KEY NAME RPAREN','problem_def',4,'p_problem_def','pddlparser.py',736),
  ('objects_def -> LPAREN OBJECTS_KEY typed_constants_lst RPAREN','objects_def',4,'p_objects_def','pddlparser.py',741),
  ('init_def -> LPAREN INIT_KEY LPAREN AND_KEY ground_predicates_lst RPAREN RPAREN','init_def',7,'p_init_def','pddlparser.py',751),
  ('init_def -> LPAREN INIT_KEY ground_predicates_lst RPAREN','init_def',4,'p_init_def','pddlparser.py',752),
  ('goal_def -> LPAREN GOAL_KEY LPAREN AND_KEY ground_predicates_lst RPAREN RPAREN','goal_def',7,'p_goal_def','pddlparser.py',760),
  ('goal_def -> LPAREN GOAL_KEY ground_predicates_lst RPAREN','goal_def',4,'p_goal_def','pddlparser.py',761),
  ('type -> NAME','type',1,'p_type','pddlparser.py',769),
  ('constant -> NAME','constant',1,'p_constant','pddlparser.py',774),
]

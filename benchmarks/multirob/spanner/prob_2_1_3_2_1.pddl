;; prob_robots_servicemen_nuts_spanners_toolboxes
(define (problem prob_2_1_3_2_1)
(:domain spanner)
(:objects 
     arm1 arm2 - robot
     serviceman1 - serviceman
     nut1 nut2 nut3 - nut
     spanner1 spanner2 - spanner
     toolbox1 - toolbox
     table serviceman_site1 - location
)
(:init 
    (at arm1 table)
    (at arm2 table)
    (free arm1)
    (free arm2)
    (at serviceman1 serviceman_site1)
    (at spanner1 toolbox1)
    (at spanner2 toolbox1)
    (useable spanner1)
    (useable spanner2)
    (loose nut1)
    (loose nut2)
    (loose nut3)
    (at nut1 table)
    (at nut2 table)
    (at nut3 table)
    (size nut1 spanner1)
    (size nut2 spanner2)
    (size nut3 spanner2)
    (link toolbox1 table)
    (link table toolbox1)
    (link serviceman_site1 table)
    (link table serviceman_site1)
)
(:goal
  (and
    (tightened nut1)
    (tightened nut2)
    (tightened nut3)
)))
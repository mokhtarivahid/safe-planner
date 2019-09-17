(define (domain bus-fare)
  (:requirements :typing :strips :equality)
  (:types coin)
  (:predicates (have-1-coin) (have-2-coin) (have-3-coin) (have-fare))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

  (:action bet-coin-1 :parameters ()
     :precondition (have-1-coin)
     :effect (and (not (have-1-coin)) (have-3-coin)))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
 
  (:action bet-coin-2 :parameters ()
     :precondition (have-2-coin)
     :effect (and (not (have-2-coin)) (have-1-coin)))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

  (:action wash-car-1 :parameters ()
     :precondition (have-1-coin)
     :effect (and (not (have-1-coin)) (have-2-coin)))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

  (:action wash-car-2 :parameters ()
     :precondition (have-2-coin)
     :effect (and (not (have-2-coin)) (have-1-coin)))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

  (:action buy-fare :parameters ()
     :precondition (have-3-coin)
     :effect (and (not (have-3-coin)) (have-fare))))
 

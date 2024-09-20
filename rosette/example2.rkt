#lang rosette

(define (sum_vector v)
    (if (null? v)
        0
        (+ (car v) (sum_vector (cdr v)))))

; (sum_vector (list 1 2 3 4))

(define-symbolic e1 e2 integer?)
(define-symbolic a b integer?)

; i want to solve for a list of size 2 whose sum is same as the list above
(define sol
    (solve
        (begin
            (assert (equal? (sum_vector (list 1 2 3 4)) (sum_vector (list e1 e2))))
            ; (assert (equal? (parse (bytestream orig_parse_table)) (parse (bytestream symbolic_parse_table))))
            (assume (> e1 0))
            (assume (> e2 0)))))

sol

(evaluate (+ a b) sol)
(evaluate (+ e1 e2) sol)

; but what if I wanted something that's not possible? - sol2 should return unsat
(define sol2
    (solve
        (begin
            (assert (equal? (sum_vector (list 1)) (sum_vector (list e1 e2))))
            (assume (> e1 0))
            (assume (> e2 0)))))

sol2

; Assert: used to define conditions that must be satisfied by the solver, based on which the values can be determined by the solver
; Assume: used to define the restrictions on the input parameters
; Both are accumalated in the verification condition (vc) and evaluated in the end

#lang rosette

(define (sum_vector v)
    (if (null? v)
        0
        (+ (car v) (sum_vector (cdr v)))))

; (sum_vector (list 1 2 3 4))

(define-symbolic e1 e2 integer?)

; i want to solve for a list of size 2 whose sum is same as the list above
(define sol
    (solve
        (begin
            (assume (equal? (sum_vector (list 1 2 3 4)) (sum_vector (list e1 e2))))
            (assume (> e1 0))
            (assume (> e2 0)))))

sol

; but what if I wanted something that's not possible? - sol2 should return unsat
(define sol2
    (solve
        (begin
            (assume (equal? (sum_vector (list 1)) (sum_vector (list e1 e2))))
            (assume (> e1 0))
            (assume (> e2 0)))))

sol2

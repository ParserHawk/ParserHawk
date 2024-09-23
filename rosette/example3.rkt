#lang rosette

;; program to check if classes and objects play spoilsport when using rosette's solve construct

(define my-class%
  (class object%
    (init-field a b)
    
    ;; Constructor
    (super-new)

    (define/public (get-a) a)
    (define/public (get-b) b)

    ;; Method to get tcam
    (define/public (get-sum)
      (list (+ a b) (- a b) (+ a 2))))
  )

(define sum-result (list 15 5 12))
(define-symbolic a-sym b-sym integer?)


(define obj (new my-class%
                      [a a-sym]
                      [b b-sym]))

(define sol
    (solve
        (begin
            (assert (equal? sum-result (send obj get-sum)))
            )))

sol
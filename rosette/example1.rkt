#lang rosette

; int32? is a shorthand for the type (bitvector 32).
(define int32? (bitvector 32))

; int32 takes as input an integer literal and returns
; the corresponding 32-bit bitvector value.
(define (int32 i)
    (bv i int32?))

(define-symbolic l h int32?)

(define (bvmid lo hi)  ; (lo + hi) / 2
    (bvsdiv (bvadd lo hi) (int32 2)))

(define (bvmid-fast lo hi)
    (bvlshr (bvadd hi lo) (bv 1 32)))

(define sol
    (solve
        (begin
        (assume (not (equal? l h)))
        (assume (bvsle (int32 0) l))
        (assume (bvsle l h))
        (assert (equal? (bvand l h) (bvmid-fast l h))))))

sol

#lang rosette

(define tcam-row%
  (class object%
    (init-field current-header lookup-val next-header extract-len next-lookup-offset lookup-phv-indices next-lookup-offsets-phv)
    
    ;; Constructor
    (super-new)

    ;; Method to get current-header
    (define/public (get-current-header)
      current-header)
    
    ;; Method to get lookup-val
    (define/public (get-lookup-val)
      lookup-val)
    
    ;; Method to get next-header
    (define/public (get-next-header)
      next-header)

    ;; Method to get extract-len
    (define/public (get-extract-len)
      extract-len)
    
    ;; Method to get next-lookup-offset
    (define/public (get-next-lookup-offset)
      next-lookup-offset)

    ;; Method to get lookup-phv-indices
    (define/public (get-lookup-phv-indices)
      lookup-phv-indices)
    
    ;; Method to get next-lookup-offsets-phv
    (define/public (get-next-lookup-offsets-phv)
      next-lookup-offsets-phv)
  ))

;; ParserTable class
(define parser-table%
  (class object%
    (init-field tcam num-rows)
    
    ;; Constructor
    (super-new)

    ;; Method to get tcam
    (define/public (get-tcam)
      tcam)
        )
  )

(define parser%
  (class object%
    (init-field bytestream packet-header-vector parser-table cursor current-row current-header-to-match current-lookup-offset)
    
    ;; Constructor
    (super-new)
    ; (set! current-header-to-match (send (vector-ref (send parser-table get-tcam) 0) get-current-header))

    ;; Method to get packet-header-vector
    (define/public (get-packet-header-vector)
      packet-header-vector)

    (define/public (get-parser-table) parser-table)

    (define/public (execute) 
    ;   if bytestream[0:3] == lookup-val then return (list 1 (list bytestream[0:extract-len])) else return (list 0 (list))

    (cond 
      [(equal? (substring bytestream 0 3) (send (vector-ref (send parser-table get-tcam) 0) get-lookup-val)) (list 1 (list (substring bytestream 0 (send (vector-ref (send parser-table get-tcam) 0) get-extract-len))))]
      [else (list 0 (list))]
     )
    )
))

(define (create-parser-table1)
  (let* ([
          my-tcam (vector 
          (new tcam-row% [current-header "S"] [lookup-val "ABC"] [next-header "accept"] [extract-len 3] [next-lookup-offset #("*")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()]))
        ]
        [parser-table (new parser-table% [tcam my-tcam] [num-rows 1])])
    parser-table))

(define-symbolic a-sym integer?)

(define (create-symbolic-parser-table1)
  (let* ([
          my-tcam (vector 
          (new tcam-row% [current-header "S"] [lookup-val "ABC"] [next-header "accept"] [extract-len a-sym] [next-lookup-offset #("*")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()]))
        ]
        [parser-table (new parser-table% [tcam my-tcam] [num-rows 1])])
    parser-table))

(define (test-phv-1)
  (begin

  (define parser (new parser%
                      [bytestream "ABCD"]
                      [packet-header-vector #()]
                      [parser-table (create-parser-table1)]
                      [cursor 0]
                      [current-row #()]
                      [current-header-to-match ""]
                      [current-lookup-offset #()]))

    (define parser2 (new parser%
                      [bytestream "ABCSDJ"]
                      [packet-header-vector #()]
                      [parser-table (create-parser-table1)]
                      [cursor 0]
                      [current-row #()]
                      [current-header-to-match ""]
                      [current-lookup-offset #()]))

    (define parser3 (new parser%
                      [bytestream "ABCFH"]
                      [packet-header-vector #()]
                      [parser-table (create-parser-table1)]
                      [cursor 0]
                      [current-row #()]
                      [current-header-to-match ""]
                      [current-lookup-offset #()]))

  (define parser_sym (new parser%
                      [bytestream "ABCD"]
                      [packet-header-vector #()]
                      [parser-table (create-symbolic-parser-table1)]
                      [cursor 0]
                      [current-row #()]
                      [current-header-to-match ""]
                      [current-lookup-offset #()]))
  

  (define result (send parser execute))
  (define result2 (send parser2 execute))
  (define result3 (send parser3 execute))
  (define expected-value #("AB"))

  (printf "result: ~a\n" result)
  (printf "result2: ~a\n" result2)
  (printf "result3: ~a\n" result3)
;   (printf "expected-result: ~a\n" expected-value)

  (define sol
    (solve
        (begin
            (assert (equal? (send parser_sym execute) result))
            (assert (equal? (send parser_sym execute) result2))
            (assert (equal? (send parser_sym execute) result3))
            ; (assert (equal? a-sym 11))
            ; (assume (<= (send (vector-ref (send (send parser get-parser-table) get-tcam) 1) get-extract-len) 3))
            ; (assume (>= (send (vector-ref (send (send parser get-parser-table) get-tcam) 1) get-extract-len) 3))
            ; (assume (<= (send (vector-ref (send (send parser get-parser-table) get-tcam) 2) get-extract-len) 4))
            ; (assume (<= (send (vector-ref (send (send parser get-parser-table) get-tcam) 3) get-extract-len) 4))
            ; (assume (<= (send (vector-ref (send (send parser get-parser-table) get-tcam) 4) get-extract-len) 4))
            )))
  sol
  ))

(test-phv-1)
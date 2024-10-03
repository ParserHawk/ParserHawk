#lang rosette

(define (sub-list lst l r)
  (take (drop lst l) (- r l)))

(define (char-list->number char-list)
  (define (char->digit c)
    (- (char->integer c) (char->integer #\0))) ;; Convert character to its digit value
  
  (define (helper lst acc)
    (if (null? lst)
        acc
        (helper (cdr lst)
                (+ (* acc 10) (char->digit (car lst))))))  ;; Multiply accumulator by 10 and add next digit
  
  (helper char-list 0))

;; Ternary match function that takes two lists of strings/characters and matches them
; TODO: return true on all cases and eliminate this func
(define (ternary-match-and2 patterns data-list)
  (define (match-helper patterns data-list)
    
    (cond
      [(empty? data-list) #t] ; If both are empty, return #t
       
      [(not (= (length patterns) (length data-list)))
       #f] ; Return #f if lengths do not match
      
      [else
       (let upper-loop ([patterns patterns]
                        [data-list data-list])
              ;(printf "pattern: ~a" (empty? patterns))
              ;(printf "data: ~a" data-list) 
         (cond
           [(empty? patterns) #t]
           [(not (= (length (list-ref patterns 0)) (length (list-ref data-list 0))))
            #f] ; Return #f if lengths of pattern and data do not match
            
           [else
            (let loop ([p-chars (list-ref patterns 0)]
                       [d-chars (list-ref data-list 0)])
              (cond
                [(empty? p-chars) (upper-loop (list-tail patterns 1) (list-tail data-list 1))] ; If all characters matched, return #t
                [(char=? (car p-chars) #\*) (loop (cdr p-chars) (cdr d-chars))] ; Skip wildcard characters
                [(char=? (car p-chars) (car d-chars)) (loop (cdr p-chars) (cdr d-chars))] ; Check if characters match
                [else #f]))] ; Return #f if a mismatch is found
           ))]))

  (match-helper patterns data-list))

(define (ternary-match-and patterns data-list) #t)


;; Class to represent each row entry in TCAM table
;; TCAM Row class
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

;; Update the parser% class to use the `get-tcam` method
(define parser%
  (class object%
    (init-field bytestream packet-header-vector parser-table cursor current-row current-header-to-match current-lookup-offset)
    
    ;; Constructor
    (super-new)
    (set! current-header-to-match (send (list-ref (send parser-table get-tcam) 0) get-current-header))

    ;; Method to get packet-header-vector
    (define/public (get-packet-header-vector)
      packet-header-vector)

    (define/public (get-parser-table) parser-table)

    ;; Step method
    (define/public (step current-header-to-match current-lookup-offset phv updated-bytestream) ;parameters to send 
      (define extraction-done #f)
      (define (parser-table-iteration parser-table-tcam packet-header-vector)
        
        (define (phv-extraction)
          (begin 
          (if (not extraction-done) 
            
              (begin (set! extraction-done #t) 
                     (append packet-header-vector 
                      (list (sub-list updated-bytestream 0 
                        (send (list-ref parser-table-tcam 0) get-extract-len)))))
              
              packet-header-vector)
        ))

        (define (lookup-extraction)
          (define (collect-all-offsets lookup-offset-index to-lookup-all)
            (let* ([bytestream-segment (delay (sub-list updated-bytestream 0 (send (list-ref parser-table-tcam 0) get-extract-len)))]
                  [to-lookup (delay (sub-list (force bytestream-segment)
                              (char-list->number (list-ref current-lookup-offset lookup-offset-index))
                              (+ (char-list->number (list-ref current-lookup-offset lookup-offset-index))
                                  (length (list-ref (send (list-ref parser-table-tcam 0) get-lookup-val) lookup-offset-index)))))])
            (if (equal? lookup-offset-index (length current-lookup-offset)) to-lookup-all                       
            (if (not (equal? (list-ref current-lookup-offset lookup-offset-index) (string->list "*"))) 
              (collect-all-offsets (add1 lookup-offset-index) (append to-lookup-all (list (force to-lookup))))
              (collect-all-offsets (add1 lookup-offset-index) to-lookup-all)
            )))
          )
          (collect-all-offsets 0 (list))
        )

        (define (process-table)
          (if (ternary-match-and (send (list-ref parser-table-tcam 0) get-lookup-val) (lookup-extraction))
            (begin 
            ; (printf "ternary match\n")
            (if (equal? (send (list-ref parser-table-tcam 0) get-next-header) (string->list "accept"))
              (list 2 (phv-extraction) (send (list-ref parser-table-tcam 0) get-extract-len) (string->list "") (list))
              (list 1 (phv-extraction) (send (list-ref parser-table-tcam 0) get-extract-len) (send (list-ref parser-table-tcam 0) get-next-header) (send (list-ref parser-table-tcam 0) get-next-lookup-offset))))
            (parser-table-iteration (list-tail parser-table-tcam 1) (phv-extraction))
            )
        )

        ; (printf "~a\n" (list-ref parser-table-tcam 0))

        (if (empty? parser-table-tcam) (list 0 packet-header-vector (string->list "") (list))
          (if (equal? (send (list-ref parser-table-tcam 0) get-current-header) current-header-to-match) (process-table) (parser-table-iteration (list-tail parser-table-tcam 1) packet-header-vector))

        ; (parser-table-iteration (add1 tcam-row-number) parser-table-tcam (phv-extraction))
        ))
      (parser-table-iteration (send parser-table get-tcam) phv))

    ;; Execute method
      (define/public (execute) ;return (parsing_code, phv)
        (define (my-func input-bytestream current-header-to-match current-lookup-offset phv)
          (let ([my-status (delay (step current-header-to-match current-lookup-offset phv input-bytestream))]) ;my-status: (return code, phv, extract-len, current-header-to-match, current-lookup-offset)
            ; (printf "step return: ~a" my-status)
              (cond
                [(= (length input-bytestream) 0) (list 0 phv)]
                [(= (list-ref (force my-status) 0) 0) (list 0 (list-ref (force my-status) 1))] ; Parsing error
                [(and (= (list-ref (force my-status) 0) 1) (not (equal? (list-ref (force my-status) 2) (string->list "*"))))
                  (let ([extract-len (list-ref (force my-status) 2)])
                    (if (>= extract-len (length input-bytestream)) (my-func (list) (list) (list) (list-ref (force my-status) 1))
                    (my-func (sub-list input-bytestream extract-len (length input-bytestream)) (list-ref (force my-status) 3) (list-ref (force my-status) 4) (list-ref (force my-status) 1))))] ; Continue parsing
                [(= (list-ref (force my-status) 0) 2) (list 1 (list-ref (force my-status) 1))])))
        (my-func bytestream current-header-to-match (list) (list)))))      

;; Function to create the parser table
(define (create-parser-table1)
  (let* ([
          my-tcam (list 
          (new tcam-row% [current-header (string->list "S")] [lookup-val `(, (string->list "*"))] [next-header (string->list "A")] [extract-len 0] [next-lookup-offset `(, (string->list "0"))] [lookup-phv-indices '()] [next-lookup-offsets-phv '()])
          (new tcam-row% [current-header (string->list "A")] [lookup-val `(, (string->list "*A"))] [next-header (string->list "B")] [extract-len 3] [next-lookup-offset `(, (string->list "*"))] [lookup-phv-indices '()] [next-lookup-offsets-phv '()])
          (new tcam-row% [current-header (string->list "A")] [lookup-val `(, (string->list "*B"))] [next-header (string->list "C")] [extract-len 3] [next-lookup-offset `(, (string->list "*"))] [lookup-phv-indices '()] [next-lookup-offsets-phv '()])
          (new tcam-row% [current-header (string->list "B")] [lookup-val `(, (string->list "*"))] [next-header (string->list "accept")] [extract-len 1] [next-lookup-offset `(, (string->list "*"))] [lookup-phv-indices '()] [next-lookup-offsets-phv '()])
          (new tcam-row% [current-header (string->list "C")] [lookup-val `(, (string->list "*"))] [next-header (string->list "accept")] [extract-len 2] [next-lookup-offset `(, (string->list "*"))] [lookup-phv-indices '()] [next-lookup-offsets-phv '()])
          
          ; (new tcam-row% [current-header "S"] [lookup-val #("*")] [next-header "A"] [extract-len 0] [next-lookup-offset #("0")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()])
          ; (new tcam-row% [current-header "A"] [lookup-val #("*A")] [next-header "B"] [extract-len 3] [next-lookup-offset #("*")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()])
          ; (new tcam-row% [current-header "A"] [lookup-val #("*B")] [next-header "C"] [extract-len 3] [next-lookup-offset #("*")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()])
          ; (new tcam-row% [current-header "B"] [lookup-val #("*")] [next-header "accept"] [extract-len 1] [next-lookup-offset #("*")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()])
          ; (new tcam-row% [current-header "C"] [lookup-val #("*")] [next-header "accept"] [extract-len 1] [next-lookup-offset #("*")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()])
          )
        ]
        [parser-table (new parser-table% [tcam my-tcam] [num-rows 1])])

    parser-table))

(define-symbolic ext-len1 ext-len2 ext-len3 ext-len4 ext-len5 integer?)
; (set! a-sym 10)
;...

(define (create-symbolic-parser-table1)
  (let* ([
          my-tcam (list 
          (new tcam-row% [current-header (string->list "S")] [lookup-val `(, (string->list "*"))] [next-header (string->list "A")] [extract-len ext-len1] [next-lookup-offset `(, (string->list "0"))] [lookup-phv-indices '()] [next-lookup-offsets-phv '()])
          (new tcam-row% [current-header (string->list "A")] [lookup-val `(, (string->list "*A"))] [next-header (string->list "B")] [extract-len ext-len2] [next-lookup-offset `(, (string->list "*"))] [lookup-phv-indices '()] [next-lookup-offsets-phv '()])
          (new tcam-row% [current-header (string->list "A")] [lookup-val `(, (string->list "*B"))] [next-header (string->list "C")] [extract-len ext-len3] [next-lookup-offset `(, (string->list "*"))] [lookup-phv-indices '()] [next-lookup-offsets-phv '()])
          (new tcam-row% [current-header (string->list "B")] [lookup-val `(, (string->list "*"))] [next-header (string->list "accept")] [extract-len ext-len4] [next-lookup-offset `(, (string->list "*"))] [lookup-phv-indices '()] [next-lookup-offsets-phv '()])
          (new tcam-row% [current-header (string->list "C")] [lookup-val `(, (string->list "*"))] [next-header (string->list "accept")] [extract-len ext-len5] [next-lookup-offset `(, (string->list "*"))] [lookup-phv-indices '()] [next-lookup-offsets-phv '()])
          ; (new tcam-row% [current-header "S"] [lookup-val #("*")] [next-header "accept"] [extract-len 1] [next-lookup-offset #("*")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()])
          
          ; (new tcam-row% [current-header "S"] [lookup-val #("*")] [next-header "A"] [extract-len 0] [next-lookup-offset #("0")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()])
          ; (new tcam-row% [current-header "A"] [lookup-val #("*A")] [next-header "B"] [extract-len a] [next-lookup-offset #("*")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()])
          ; (new tcam-row% [current-header "A"] [lookup-val #("*B")] [next-header "C"] [extract-len 3] [next-lookup-offset #("*")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()])
          ; (new tcam-row% [current-header "B"] [lookup-val #("*")] [next-header "accept"] [extract-len 1] [next-lookup-offset #("*")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()])
          ; (new tcam-row% [current-header "C"] [lookup-val #("*")] [next-header "accept"] [extract-len 1] [next-lookup-offset #("*")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()])
          )
        ]
        [parser-table (new parser-table% [tcam my-tcam] [num-rows 1])])

    parser-table))


;; Test function for parsing and verifying the packet header vector
(define (test-phv-1)
  ;; Create the parser table
  (begin

  ;; Initialize the parser with the bytestream "2AC1" and the created parser table
  (define parser (new parser%
                      [bytestream (string->list "2AC1")]
                      [packet-header-vector '()]
                      [parser-table (create-parser-table1)]
                      [cursor 0]
                      [current-row '()]
                      [current-header-to-match ""]
                      [current-lookup-offset '()]))

  (define parser_sym (new parser%
                      [bytestream (string->list "2AC1")]
                      [packet-header-vector '()]
                      [parser-table (create-symbolic-parser-table1)]
                      [cursor 0]
                      [current-row '()]
                      [current-header-to-match ""]
                      [current-lookup-offset '()]))
  
  (define parser2 (new parser%
                      [bytestream (string->list "2BXQ00")]
                      [packet-header-vector '()]
                      [parser-table (create-parser-table1)]
                      [cursor 0]
                      [current-row '()]
                      [current-header-to-match ""]
                      [current-lookup-offset '()]))

  (define parser2_sym (new parser%
                      [bytestream (string->list "2BXQ00")]
                      [packet-header-vector '()]
                      [parser-table (create-symbolic-parser-table1)]
                      [cursor 0]
                      [current-row '()]
                      [current-header-to-match ""]
                      [current-lookup-offset '()]))

  ;; Get the result, which is the packet header vector
  ; (define result (send parser execute))

  ;; Define the expected value
  ; (define expected-value #("2"))

  (printf "result1: ~a\n" (send parser execute))
  (printf "result2: ~a\n" (send parser2 execute))
  ; (printf "expected-result: ~a\n" expected-value)

  ;; Assert that the result matches the expected value
  ; (equal? (list-ref result 1) expected-value)

  (define sol
    (solve
        (begin
            (assert (equal? (send parser execute) (send parser_sym execute)))
            (assert (equal? (send parser2 execute) (send parser2_sym execute)))
            ; (assert (equal? a-sym 11))
            ; (assume (<= (send (list-ref (send (send parser get-parser-table) get-tcam) 1) get-extract-len) 3))
            ; (assume (>= (send (list-ref (send (send parser get-parser-table) get-tcam) 1) get-extract-len) 3))
            ; (assume (<= (send (list-ref (send (send parser get-parser-table) get-tcam) 2) get-extract-len) 4))
            ; (assume (<= (send (list-ref (send (send parser get-parser-table) get-tcam) 3) get-extract-len) 4))
            ; (assume (<= (send (list-ref (send (send parser get-parser-table) get-tcam) 4) get-extract-len) 4))
            )))

  ; (evaluate ext-len2 sol)
  ; (printf "Solution for a: ~a\n" (sol 'a))
  sol
  ))

;; Call the test function to run it
(test-phv-1)

; TODO: 
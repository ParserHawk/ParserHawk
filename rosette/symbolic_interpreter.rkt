#lang rosette

;; Ternary match function that takes two lists of strings/characters and matches them
(define (ternary-match-and patterns data-list)
  (define (match-helper patterns data-list)
    
    (cond
      [(vector-empty? data-list) #t] ; If both are empty, return #t
       
      [(not (= (vector-length patterns) (vector-length data-list)))
       #f] ; Return #f if lengths do not match
      
      [else
       (let upper-loop ([patterns patterns]
                        [data-list data-list])
              ;(printf "pattern: ~a" (empty? patterns))
              ;(printf "data: ~a" data-list) 
         (cond
           [(vector-empty? patterns) #t]
           [(not (= (string-length (vector-ref patterns 0)) (string-length (vector-ref data-list 0))))
            #f] ; Return #f if lengths of pattern and data do not match
            
           [else
            (let loop ([p-chars (string->list (vector-ref patterns 0))]
                       [d-chars (string->list (vector-ref data-list 0))])
              (cond
                [(empty? p-chars) (upper-loop (vector-copy patterns 1) (vector-copy data-list 1))] ; If all characters matched, return #t
                [(char=? (car p-chars) #\*) (loop (cdr p-chars) (cdr d-chars))] ; Skip wildcard characters
                [(char=? (car p-chars) (car d-chars)) (loop (cdr p-chars) (cdr d-chars))] ; Check if characters match
                [else #f]))] ; Return #f if a mismatch is found
           ))]))

  (match-helper patterns data-list))


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
    
    ; ;; Method to add a TCAM row
    ; (define/public (add-tcam-row row)
    ;   (set! tcam (vector-append tcam (vector row))))
    
    ;; Ensure rows are legal
    ; (define/public (validate)
    ;   (define present-lookup-offset (send (first tcam) next-lookup-offset))
    ;   (for/or ([i (in-range 1 num-rows)])
    ;     (if (> present-lookup-offset (send (list-ref tcam i) extract-len))
    ;         #f
    ;         (set! present-lookup-offset (send (list-ref tcam i) next-lookup-offset))))
    ;   (let ([source-headers (map (λ (row) (send row current-header)) tcam)]
    ;         [target-headers (map (λ (row) (send row next-header)) tcam)])
    ;     (equal? source-headers target-headers)))
        )
  )

;; Update the parser% class to use the `get-tcam` method
(define parser%
  (class object%
    (init-field bytestream packet-header-vector parser-table cursor current-row current-header-to-match current-lookup-offset)
    
    ;; Constructor
    (super-new)
    (set! current-header-to-match (send (vector-ref (send parser-table get-tcam) 0) get-current-header))

    ;; Method to get packet-header-vector
    (define/public (get-packet-header-vector)
      packet-header-vector)

    (define/public (get-parser-table) parser-table)

    ;; Step method
    (define/public (step current-header-to-match current-lookup-offset phv updated-bytestream) ;parameters to send 
      (define extraction-done #f)
      (define (parser-table-iteration parser-table-tcam packet-header-vector)
        
        (define (phv-extraction)
          (begin (printf "phv: ~a\n" packet-header-vector)

          ; TODO: fix this to return phv in all failure cases as well
          (if (not extraction-done) 
            (if (not (equal? (send (vector-ref parser-table-tcam 0) get-extract-len) "*"))
              (begin (set! extraction-done #t) 
                     (vector-append packet-header-vector 
                      (vector (substring updated-bytestream 0 
                        (string->number (send (vector-ref parser-table-tcam 0) get-extract-len)))))) 
              packet-header-vector) 
              packet-header-vector)
        ))

        (define (lookup-extraction)
          (define (collect-all-offsets lookup-offset-index to-lookup-all)
            (let* ([bytestream-segment (delay (substring updated-bytestream 0 (string->number (send (vector-ref parser-table-tcam 0) get-extract-len))))]
                  [to-lookup (delay (substring (force bytestream-segment)
                              (string->number (vector-ref current-lookup-offset lookup-offset-index))
                              (+ (string->number (vector-ref current-lookup-offset lookup-offset-index))
                                  (string-length (vector-ref (send (vector-ref parser-table-tcam 0) get-lookup-val) lookup-offset-index)))))])
            (if (equal? lookup-offset-index (vector-length current-lookup-offset)) to-lookup-all                       
            (if (not (equal? (vector-ref current-lookup-offset lookup-offset-index) "*")) 
              (collect-all-offsets (add1 lookup-offset-index) (vector-append to-lookup-all (vector (force to-lookup))))
              (collect-all-offsets (add1 lookup-offset-index) to-lookup-all)
            )))
          )
          (collect-all-offsets 0 (vector))
        )

        (define (process-table)
          ; if ternary match and accept then return code = 2
          (printf "~a\n" (send (vector-ref parser-table-tcam 0) get-lookup-val))
          (if (ternary-match-and (send (vector-ref parser-table-tcam 0) get-lookup-val) (lookup-extraction))
            (begin (printf "ternary match\n")
            (if (equal? (send (vector-ref parser-table-tcam 0) get-next-header) "accept")
              (list 2 (phv-extraction) (send (vector-ref parser-table-tcam 0) get-extract-len) "" (vector))
              (list 1 (phv-extraction) (send (vector-ref parser-table-tcam 0) get-extract-len) (send (vector-ref parser-table-tcam 0) get-next-header) (send (vector-ref parser-table-tcam 0) get-next-lookup-offset))))
            (parser-table-iteration (vector-copy parser-table-tcam 1) (phv-extraction))
            )
        )

        ; (printf "~a\n" (vector-ref parser-table-tcam 0))

        (if (vector-empty? parser-table-tcam) (list 0 packet-header-vector "" (vector))
          (if (equal? (send (vector-ref parser-table-tcam 0) get-current-header) current-header-to-match) (process-table) (parser-table-iteration (vector-copy parser-table-tcam 1) packet-header-vector))

        ; (parser-table-iteration (add1 tcam-row-number) parser-table-tcam (phv-extraction))
        ))
      (parser-table-iteration (send parser-table get-tcam) phv))

    ;; Execute method
      (define/public (execute) ;return (parsing_code, phv)
        (define (my-func input-bytestream current-header-to-match current-lookup-offset phv)
          (let ([my-status (delay (step current-header-to-match current-lookup-offset phv input-bytestream))]) ;my-status: (return code, phv, extract-len, current-header-to-match, current-lookup-offset)
            ; (printf "step return: ~a" my-status)
              (cond
                [(= (string-length input-bytestream) 0) (list 0 phv)]
                [(= (list-ref (force my-status) 0) 0) (list 0 (list-ref (force my-status) 1))] ; Parsing error
                [(and (= (list-ref (force my-status) 0) 1) (not (equal? (list-ref (force my-status) 2) "*")))
                  (let ([extract-len (string->number (list-ref (force my-status) 2))])
                    (if (>= extract-len (string-length input-bytestream)) (my-func "" "" (vector) (list-ref (force my-status) 1))
                    (my-func (substring input-bytestream extract-len) (list-ref (force my-status) 3) (list-ref (force my-status) 4) (list-ref (force my-status) 1))))] ; Continue parsing
                [(= (list-ref (force my-status) 0) 2) (printf "accepted\n") (list 1 (list-ref (force my-status) 1))])))
        (my-func bytestream current-header-to-match (vector) (vector)))))      

;; Function to create the parser table
(define (create-parser-table1)
  (let* ([
          my-tcam (vector 
          (new tcam-row% [current-header "S"] [lookup-val #("*")] [next-header "A"] [extract-len "0"] [next-lookup-offset #("0")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()])
          (new tcam-row% [current-header "A"] [lookup-val #("*A")] [next-header "B"] [extract-len "3"] [next-lookup-offset #("*")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()])
          (new tcam-row% [current-header "A"] [lookup-val #("*B")] [next-header "C"] [extract-len "3"] [next-lookup-offset #("*")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()])
          (new tcam-row% [current-header "B"] [lookup-val #("*")] [next-header "accept"] [extract-len "1"] [next-lookup-offset #("*")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()])
          (new tcam-row% [current-header "C"] [lookup-val #("*")] [next-header "D"] [extract-len "2"] [next-lookup-offset #("1")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()])
          (new tcam-row% [current-header "D"] [lookup-val #("11")] [next-header "E"] [extract-len "4"] [next-lookup-offset #("*")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()])
          (new tcam-row% [current-header "D"] [lookup-val #("01")] [next-header "F"] [extract-len "4"] [next-lookup-offset #("*")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()])
          (new tcam-row% [current-header "E"] [lookup-val #("*")] [next-header "accept"] [extract-len "5"] [next-lookup-offset #("*")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()])
          (new tcam-row% [current-header "F"] [lookup-val #("*")] [next-header "accept"] [extract-len "6"] [next-lookup-offset #("*")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()]))
        ]
        [parser-table (new parser-table% [tcam my-tcam] [num-rows 9])])

    ; (send parser-table add-tcam-row (new tcam-row% [current-header "S"] [lookup-val #("*")] [next-header "A"] [extract-len "*"] [next-lookup-offset #("0")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()]))
    ; (send parser-table add-tcam-row (new tcam-row% [current-header "A"] [lookup-val #("*A")] [next-header "B"] [extract-len "3"] [next-lookup-offset #("*")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()]))
    ; (send parser-table add-tcam-row (new tcam-row% [current-header "A"] [lookup-val #("*B")] [next-header "C"] [extract-len "3"] [next-lookup-offset #("*")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()]))
    ; (send parser-table add-tcam-row (new tcam-row% [current-header "B"] [lookup-val #("*")] [next-header "accept"] [extract-len "1"] [next-lookup-offset #("*")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()]))
    ; (send parser-table add-tcam-row (new tcam-row% [current-header "C"] [lookup-val #("*")] [next-header "D"] [extract-len "2"] [next-lookup-offset #("1")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()]))
    ; (send parser-table add-tcam-row (new tcam-row% [current-header "D"] [lookup-val #("11")] [next-header "E"] [extract-len "4"] [next-lookup-offset #("*")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()]))
    ; (send parser-table add-tcam-row (new tcam-row% [current-header "D"] [lookup-val #("01")] [next-header "F"] [extract-len "4"] [next-lookup-offset #("*")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()]))
    ; (send parser-table add-tcam-row (new tcam-row% [current-header "E"] [lookup-val #("*")] [next-header "accept"] [extract-len "5"] [next-lookup-offset #("*")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()]))
    ; (send parser-table add-tcam-row (new tcam-row% [current-header "F"] [lookup-val #("*")] [next-header "accept"] [extract-len "6"] [next-lookup-offset #("*")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()]))
    parser-table))

;; Test parsing function
; (define (test-parsing-1)
;   (define parser-table (create-parser-table1))
;   (define parser (new parser% [bytestream "2AC1"] [packet-header-vector '()] [parser-table parser-table] [cursor 0] [current-row '()] [current-header-to-match ""] [current-lookup-offset '()]))
;   (define result (send parser execute))
;   (define expected-value 1)
;   (printf "result: ~a\n" result)
;   (printf "expected-value: ~a\n" expected-value)
;   (assert (equal? result expected-value)))

; ;; Run the test
; (test-parsing-1)

;; Test function for parsing and verifying the packet header vector
(define (test-phv-1)
  ;; Create the parser table
  (begin

  ;; Initialize the parser with the bytestream "2AC1" and the created parser table
  (define parser (new parser%
                      [bytestream "2AC1"]
                      [packet-header-vector #()]
                      [parser-table (create-parser-table1)]
                      [cursor 0]
                      [current-row #()]
                      [current-header-to-match ""]
                      [current-lookup-offset #()]))

  (printf "table length:~a\n" (vector-length (send (send parser get-parser-table) get-tcam)))
  ;; Execute the parser
  

  ;; Get the result, which is the packet header vector
  (define result (send parser execute))

  ;; Define the expected value
  (define expected-value #("" "2AC" "1"))

  ;; Print the result and expected value
  (printf "whole result: ~a\n" result)
  (printf "result: ~a\n" (list-ref result 1))
  (printf "first elem: ~a\n" (vector-ref (list-ref result 1) 1))
  (printf "result len: ~a\n" (length result))
  (printf "expected-value: ~a\n" expected-value)

  ;; Assert that the result matches the expected value
  (equal? (list-ref result 1) expected-value)))

;; Call the test function to run it
(test-phv-1)
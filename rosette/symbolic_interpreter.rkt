#lang rosette
(require racket/control)
; #lang racket
; (require racket/list)

;; Ternary match function that takes two lists of strings/characters and matches them
(define (ternary-match-and patterns data-list)
  (define (match-helper patterns data-list)
    (cond
      [(empty? data-list) #t] ; If both are empty, return #t
       
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
      ; ]))

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
    
    ;; Method to add a TCAM row
    (define/public (add-tcam-row row)
      (set! tcam (vector-append tcam (vector row))))
    
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
    (define/public (step)
      (define extraction-done #f)
      (define bytestream-segment "")
      (define tcam-length (vector-length (send parser-table get-tcam)))
      (define final-status -1)
      (printf "length outside loop ~a\n" tcam-length)

      (for ([tcam-row (+ 1 tcam-length)])
        (printf "inside step loop: ~a, ~b\n" tcam-row tcam-length)
        (cond [(equal? tcam-row tcam-length) (begin (printf "exiting\n\n") (set! final-status 0) (break))]
              [else (begin
                      (printf "inside else: ~a\n" tcam-row)
                      (cond [(equal? (send (vector-ref (send parser-table get-tcam) tcam-row) get-current-header) current-header-to-match)
                            (begin (when (equal? extraction-done #t)
                                    (when (not (equal? (send (vector-ref (send parser-table get-tcam) tcam-row) get-extract-len) "*"))
                                    (begin (set! bytestream-segment
                                                  (substring bytestream
                                                            cursor
                                                            (+ cursor (string->number (send (vector-ref (send parser-table get-tcam) tcam-row) get-extract-len)))))
                                            (set! packet-header-vector (vector-append packet-header-vector (vector bytestream-segment)))
                                            (set! extraction-done #t))))
                                  (define to-lookup-all #())
                                  (for ([lookup-offset-index (vector-length current-lookup-offset)])
                                    (begin (define to-lookup "*")
                                            (when (not (equal? (vector-ref current-lookup-offset lookup-offset-index) "*"))
                                              (begin
                                                (vector-set! current-lookup-offset lookup-offset-index (string->number (vector-ref current-lookup-offset lookup-offset-index)))
                                                (set! to-lookup
                                                      (substring bytestream-segment
                                                                (vector-ref current-lookup-offset lookup-offset-index)
                                                                (+ (vector-ref current-lookup-offset lookup-offset-index)
                                                                    (string-length (vector-ref (send (vector-ref (send parser-table get-tcam) tcam-row) get-lookup-val) lookup-offset-index)))))
                                                (set! to-lookup-all (vector-append to-lookup-all (vector to-lookup)))
                                                ))))
                                  (when (ternary-match-and (send (vector-ref (send parser-table get-tcam) tcam-row) get-lookup-val) to-lookup-all)
                                  (printf "found match: ~a" tcam-row)
                                    (begin (if (equal? (send (vector-ref (send parser-table get-tcam) tcam-row) get-next-header) "accept") (begin (set! final-status 2) (break))
                                                (begin (set! current-header-to-match (send (vector-ref (send parser-table get-tcam) tcam-row) get-next-header))
                                                      (set! current-lookup-offset (send (vector-ref (send parser-table get-tcam) tcam-row) get-next-lookup-offset))
                                                      (set! current-row tcam-row) (set! final-status 1) (break)))))
                                  )]))])))

    ;; Execute method
      (define/public (execute)
        (let my-func ()
          (when (< cursor (string-length bytestream))
            (let ([my-status (send this step)])
            (printf "step return: ~a" my-status)
              (cond
                [(= my-status 0) 0] ; Parsing error
                [(= my-status 1)
                (let* (
                      [current-row-tcam (vector-ref (send parser-table get-tcam) current-row)]
                      [curr-length (send current-row-tcam extract-len)]
                      [int-length (if (equal? curr-length "*") 0 (string->number curr-length))])
                  (set! cursor (+ cursor int-length))
                  (my-func))] ; Continue parsing
                [(= my-status 2) 1])))))
                                ))

;; Function to create the parser table
(define (create-parser-table1)
  (let ([parser-table (new parser-table% [tcam #()] [num-rows 9])])
    ;; Add TCAM rows to the parser table
    (send parser-table add-tcam-row (new tcam-row% [current-header "S"] [lookup-val #("*")] [next-header "A"] [extract-len "*"] [next-lookup-offset #("0")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()]))
    (send parser-table add-tcam-row (new tcam-row% [current-header "A"] [lookup-val #("*A")] [next-header "B"] [extract-len "3"] [next-lookup-offset #("*")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()]))
    (send parser-table add-tcam-row (new tcam-row% [current-header "A"] [lookup-val #("*B")] [next-header "C"] [extract-len "3"] [next-lookup-offset #("*")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()]))
    (send parser-table add-tcam-row (new tcam-row% [current-header "B"] [lookup-val #("*")] [next-header "accept"] [extract-len "1"] [next-lookup-offset #("*")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()]))
    (send parser-table add-tcam-row (new tcam-row% [current-header "C"] [lookup-val #("*")] [next-header "D"] [extract-len "2"] [next-lookup-offset #("1")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()]))
    (send parser-table add-tcam-row (new tcam-row% [current-header "D"] [lookup-val #("11")] [next-header "E"] [extract-len "4"] [next-lookup-offset #("*")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()]))
    (send parser-table add-tcam-row (new tcam-row% [current-header "D"] [lookup-val #("01")] [next-header "F"] [extract-len "4"] [next-lookup-offset #("*")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()]))
    (send parser-table add-tcam-row (new tcam-row% [current-header "E"] [lookup-val #("*")] [next-header "accept"] [extract-len "5"] [next-lookup-offset #("*")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()]))
    (send parser-table add-tcam-row (new tcam-row% [current-header "F"] [lookup-val #("*")] [next-header "accept"] [extract-len "6"] [next-lookup-offset #("*")] [lookup-phv-indices #()] [next-lookup-offsets-phv #()]))
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
  (define parser-table (create-parser-table1))

  ;; Initialize the parser with the bytestream "2AC1" and the created parser table
  (define parser (new parser%
                      [bytestream "2AC1"]
                      [packet-header-vector #()]
                      [parser-table parser-table]
                      [cursor 0]
                      [current-row #()]
                      [current-header-to-match ""]
                      [current-lookup-offset #()]))

  (printf "table length:~a\n" (vector-length (send (send parser get-parser-table) get-tcam)))
  ;; Execute the parser
  (send parser execute)

  ;; Get the result, which is the packet header vector
  (define result (send parser get-packet-header-vector))

  ;; Define the expected value
  (define expected-value #("2AC" "1"))

  ;; Print the result and expected value
  (printf "result: ~a\n" result)
  (printf "expected-value: ~a\n" expected-value)

  ;; Assert that the result matches the expected value
  (equal? result expected-value)))

;; Call the test function to run it
(test-phv-1)
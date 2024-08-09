#lang rosette

(require racket/list)

;; takes two lists as inputs and ternary matches each element against each other
(define (ternary-match-and patterns data-list)
  (if (empty? data-list)
      #t
      (if (not (= (length patterns) (length data-list)))
          #f
          (for/or ([pattern patterns] [data data-list])
            (if (not (= (length pattern) (length data)))
                #f
                (for/or ([p-char pattern] [d-char data])
                  (cond
                    [(equal? p-char #\*) #t]  ; Wildcard matches any character
                    [(not (equal? p-char d-char)) #f])))))))

;; Class to represent each row entry in TCAM table
(define tcam-row%
  (class object%
    (init-field current-header lookup-val next-header extract-len next-lookup-offset lookup-phv-indices next-lookup-offsets-phv)
    
    ;; Constructor
    (super-new)))

;; ParserTable class
(define parser-table%
  (class object%
    (init-field tcam num-rows)
    
    ;; Constructor
    (super-new)

    ;; Ensure rows are legal
    (define/public (validate)
      (define present-lookup-offset (send (first tcam) next-lookup-offset))
      (for/or ([i (in-range 1 num-rows)])
        (if (> present-lookup-offset (send (list-ref tcam i) extract-len))
            #f
            (set! present-lookup-offset (send (list-ref tcam i) next-lookup-offset))))
      (let ([source-headers (map (λ (row) (send row current-header)) tcam)]
            [target-headers (map (λ (row) (send row next-header)) tcam)])
        (equal? source-headers target-headers)))

    ;; Display the parser table as rows of dictionaries
    ; (define/override (to-string)
    ;   (string-join
    ;    (map (λ (row) (format "~a" (object->vector row))) tcam)
    ;    "\n"))))
  ))

;; Parser class
(define parser%
  (class object%
    (init-field bytestream packet-header-vector parser-table cursor current-row current-header-to-match current-lookup-offset)
    
    ;; Constructor
    (super-new)
    (set! current-header-to-match (send (first (send parser-table tcam)) current-header))
    
    ;; Execute method
    (define/public (execute)
      (let loop ()
        (when (< cursor (length bytestream))
          (let ([status (send this step)])
            (cond
              [(= status 0) 0] ; Parsing error
              [(= status 1)
               (when (not (equal? (send (list-ref (send parser-table tcam) current-row) extract-len) "*"))
                 (set! cursor (+ cursor (string->number (send (list-ref (send parser-table tcam) current-row) extract-len)))))
               (loop)] ; Continue parsing
              [(= status 2) 1]))))) ; Accept state reached

    ;; Step method
    (define/public (step)
      (define extraction-done #f)
      (define bytestream-segment "")
      (for/or ([tcam-row (send parser-table tcam)])
        (when (equal? (send tcam-row current-header) current-header-to-match)
          (unless extraction-done
            (unless (equal? (send tcam-row extract-len) "*")
              (set! bytestream-segment (substring bytestream cursor (+ cursor (string->number (send tcam-row extract-len)))))
              (set! packet-header-vector (append packet-header-vector (list bytestream-segment)))
              (set! extraction-done #t)))
          (define to-lookup-all '())
          (for ([lookup-offset-index (in-range (length current-lookup-offset))])
            (let ([to-lookup "*"])
                (unless (equal? (list-ref current-lookup-offset lookup-offset-index) "*")
                (set! current-lookup-offset
                        (list-set current-lookup-offset
                                lookup-offset-index
                                (string->number (list-ref current-lookup-offset lookup-offset-index))))
                (set! to-lookup (substring bytestream-segment 
                                 (list-ref current-lookup-offset lookup-offset-index) 
                                 (+ (list-ref current-lookup-offset lookup-offset-index) 
                                    (length (list-ref (send tcam-row lookup-val) lookup-offset-index)))))
      (set! to-lookup-all (append to-lookup-all (list to-lookup)))))
(when (ternary-match-and (send tcam-row lookup-val) to-lookup-all)
            (if (equal? (send tcam-row next-header) "accept")
                2 ; Accept state reached
                (begin
                  (set! current-header-to-match (send tcam-row next-header))
                  (set! current-lookup-offset (send tcam-row next-lookup-offset))
                  (set! current-row tcam-row)
                  1)))) ; Valid transition, continue parsing
      0)) ; Parsing fails

    ;; Getters and Setters (as needed)
    )))


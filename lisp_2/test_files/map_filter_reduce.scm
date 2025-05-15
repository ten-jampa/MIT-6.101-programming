(begin
    (define null? 
        (lambda (List)
            (if (equal? (length List) 0)
                #t
                #f
            )
        )
    )

    (define map
        (lambda (Function List)
            (if (null? List) 
                ()
                (cons (Function (car List)) (map Function (cdr List)))
            )
        )
    )

    (define filter
        (lambda (Function List)
            (if (null? List)
                ()
                (if (Function (car List))
                    (cons (car List) (filter Function (cdr List)))
                    (filter Function (cdr List))
                )
            )
        )
    )

    (define reduce
        (lambda (Function List InitVal)
            (if (null? List)
                InitVal
                (reduce Function (cdr List) (Function InitVal (car List)))
            )
        )
    )
)
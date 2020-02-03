;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; connect 
;;
;;	pb0 <- sw0
;;	pb1 <- sw1
;;	pb2 -> led0
;;	pb4 -> led1
;;
;;	light lights on rising edge of switch
;;	keep light lit for timeout period after

	.include "tn12def.inc"

	rjmp	main	; reset
	rjmp	err	; ext_int0
	rjmp	err	; pin_change
	rjmp	tick	; tim0_ovf
	rjmp	err	; ee_ready (Tiny12 only)
	rjmp	err	; ana-comp

.equ	sw0	= 0
.equ	sw1	= 1
.equ	led0	= 2
.equ	led1	= 4

err:
	reti
tick:
	reti

main:
	;; setup I/Os

	sbi	DDRB,led0
	sbi	DDRB,led1
	cbi	DDRB,sw0
	cbi	DDRB,sw1

loop:
	in	r0,pinb
	sbrs	r0,sw0
	rjmp	loop2
	sbi	PORTB,led0
loop2:
	sbrs	r0,sw1
	rjmp	loop4
	cbi	PORTB,led0
loop4:
	rjmp	loop


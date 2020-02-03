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
	rjmp	main	; ext_int0
	rjmp	main	; pin_change
	rjmp	tick	; tim0_ovf
	rjmp	main	; ee_ready (Tiny12 only)
	rjmp	main	; ana-comp

.equ	sw0	= 0
.equ	sw1	= 1
.equ	led0	= 2
.equ	led1	= 4
.equ	ck1K	= (1<<CS02)|(1<<CS00)

.equ	count0	= r21 ; timeout counter for sw0/led0
.equ	count1	= r22 ; timeout counter for sw1/led1
.equ	timeout0 = 100
.equ	timeout1 = 200


main:
	;; setup I/Os

	sbi	DDRB,led0
	sbi	DDRB,led1
	cbi	DDRB,sw0
	cbi	DDRB,sw1

	;; setup timer, interrupts

	ldi	r16,ck1K
	out	TCCR0,r16

	ldi	r16,(1<<TOIE0)
	out	TIMSK,r16
	ldi	r16,(1<<TOV0)
	out	TIFR,r16
	clr	r21
	sei
loop:
	in	r0,pinb
	sbrs	r0,sw0
	rjmp	loop4
	sbi	PORTB,led0
	rjmp	loop4
loop1:
	cbi	PORTB,led0
loop2:
	sbrs	r0,sw1
	rjmp	loop3
	sbi	PORTB,led1
	rjmp	loop4
loop3:
	cbi	PORTB,led1
loop4:
	rjmp	loop

tick:
	inc	r21
	sbrs	r21,3
	rjmp	tick1
	sbi	portb,led1
	rjmp	tick2
tick1:
	cbi	portb,led1
tick2:
	reti
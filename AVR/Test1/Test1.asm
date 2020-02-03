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

;	.include "8515def.inc"
	.include "tn12def.inc"

	rjmp	main	; reset
	rjmp	error	; ext_int0
	rjmp	error	; pin_change
	rjmp	timer	; tim0_ovf
	rjmp	error	; ee_ready (Tiny12 only)
	rjmp	error	; ana-comp

.equ	sw0	= 0
.equ	sw1	= 1
.equ	led0	= 2
.equ	led1	= 4
.equ	led2	= 3

.equ	ck1K	= (1<<CS02)|(1<<CS00)
.equ	ck512	= ck1K - 1

.equ	timeout0 = 10
.equ	timeout1 = 20

;; register allocations:

.def	count0	= r20 ; timeout counter for sw0/led0
.def	count1	= r21 ; timeout counter for sw1/led1
.def	savesp 	= r17
.def	tmp 	= r16
.def	ereg	= r18
.def	ono0	= r10
.def	ono1	= r11
.def	repeat	= r22

;;;;;;;;;;; init hardware

init:

	;; setup I/Os

	sbi	DDRB,led0
	sbi	DDRB,led1
	sbi	DDRB,led2
	cbi	DDRB,sw0
	cbi	DDRB,sw1

	sbi	PORTB,led0
	sbi	PORTB,led1
	sbi	PORTB,led2

	;; setup timer, interrupts

	ldi	tmp,ck1K
	out	TCCR0,tmp

	ldi	tmp,(1<<TOIE0)
	out	TIMSK,tmp
	ldi	tmp,(1<<TOV0)
	out	TIFR,tmp

	;; clear unused interrupts

	clr	tmp
	out	GIMSK,tmp
	out	GIFR,tmp

	;; enable ints
	sei

	ret


;;;;;;;;;;;; unexpected interrupt

error:
	in	savesp,SREG
	ldi	ereg,ck512
	out	TCCR0,ereg
	out	SREG,savesp
	reti

;;;;;;;;;;;; timer interrupt

timer:
	in	savesp,SREG
	rcall	toggle1
;;	rcall	dcount1
;;	rcall	dcount0
	out	SREG,savesp
	reti

;;;;;;;;;;; main program
	
main:

;; setup stack, if there is one...

	.ifdef	RAMEND
	.ifdef	SPL
	ldi	r16,low(RAMEND)
	out	SPL,r16
	.endif
	.ifdef	SPH
	ldi	r16,high(RAMEND)
	out	SPH,r16
	.endif
	.endif

	rcall	init

loop:
	rcall	onoff0
 	rjmp	loop



;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; various actions

;; turn on led0 if sw0 is pressed
;; turn it off if sw1 is pressed

onoff0:
	in	ono0,pinb
	sbrc	ono0,sw0
	rjmp	onoff0a
	sbi	PORTB,led0
	cbi	portb,led2
;;	sei
onoff0a:
	sbrc	ono0,sw1
	rjmp	onoff0b
	cbi	PORTB,led0
	sbi	portb,led2
;;	cli
onoff0b:
	ret

;; turn on led1 if sw0 is pressed
;; turn it off if sw1 is pressed

onoff1:
	in	ono1,pinb
	sbrc	ono1,sw0
	rjmp	onoff1a
	sbi	PORTB,led1
onoff1a:
	sbrc	ono1,sw1
	rjmp	onoff1b
	cbi	PORTB,led1
onoff1b:
	ret

;; turn on led0 if count0 expires

dcount0:
	tst	count0
	breq	dcount0a
	dec	count0
	brne	dcount0a
	sbi	PORTB,led0
dcount0a:
	ret
	
;; turn on led1 if count1 expires

dcount1:
	tst	count1
	breq	dcount1a
	dec	count1
	brne	dcount1a
	sbi	PORTB,led1
dcount1a:
	ret
	
;; toggle led0

toggle0:
	inc	count0
	sbrs	count0,0
	rjmp	toggle01
	sbi	portb,led0
	rjmp	toggle02
toggle01:
	cbi	portb,led0
toggle02:
	ret	

;; toggle led1 

toggle1:
	inc	count1
	sbrs	count1,0
	rjmp	toggle11
	sbi	portb,led1
	rjmp	toggle12
toggle11:
	cbi	portb,led1
toggle12:
	ret	



;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; WetDet -- Wet Detector 
;;
;; Monitor one or more water sensors, 
;; signal alarm for a while if/when they trip, and
;; track that alarm went off.
;;
;;
.include "tn12def.inc"

;; Inputs:

.equ	dry	= 4	;; wet sensor
.equ	abort	= 3	;; enter error state

;; Outputs:

.equ	light	= 0	;; indicator light
.equ	after	= 1	;; signal during and after alarm
.equ	alarm	= 2	;; alarm signal

;; register allocations:

.def	tmp 	= r16	;; temp reg for casual use

.def	savesp 	= r17	;; save/restore SREG
.def	timetmp	= r21
.def	timelo	= r22	;; 16 bit down-counter
.def	timehi	= r23

.def	waittmp	= r24	;; for wait routine to test timer expiration

.def	state	= r26	;; present system state
.def	stcount = r27	;; counter for state led
.def	sttmp	= r28	;; temp reg for state display

.equ	st_norm	= 0x50	;; possible states...
.equ	st_trip	= 0x55	;; ... 1 => light on
.equ	st_err	= 0xF0

;; other constants

.equ	ck1K	= (1<<CS02)|(1<<CS00)
.equ	ck512	= ck1K - 1

.equ	cal_byte = 0x1ff ;; code loc where we put osc cal value

.equ	alarmtime = 50	;; raise alarm for this period of time
;.equ	initial = 0x4F	;; initial timer count

;;;;;;;;;;;; hardware interrupt vectors

	rjmp	main	; reset
	rjmp	error	; ext_int0
	rjmp	error	; pin_change
	rjmp	timer	; tim0_ovf
	rjmp	error	; ee_ready (Tiny12 only)
	rjmp	error	; ana-comp

;;;;;;;;;;;; unexpected interrupt

error:
	ori	state,st_err
	reti

;;;;;;;;;;;; timer interrupt

timer:
	in	savesp,SREG	;; save SREG

.ifdef	initial
	;; reset residual counter
	ldi	timetmp,initial
	out	TCNT0,timetmp
.endif

	;; advance life indicator
	inc	stcount
	andi	stcount,7
	mov	timetmp,stcount
	mov	sttmp,state
timer1:
	asr	sttmp
	dec	timetmp
	brpl	timer1

	brcs	timer2
	sbi	portb,light
	rjmp	timer3
timer2:
	cbi	portb,light
	rjmp	timer3

	;; decrement 16 bit timer iff >0
timer3:
	mov	timetmp,timehi
	or	timetmp,timelo
	breq	timer4
	subi	timelo,1
	sbci	timehi,0

timer4:
	out	SREG,savesp	;; restore SREG
	reti


;; wait for timer to expire

wait:	
	in	waittmp,pinb
	sbrs	waittmp,abort
	rjmp	fatal
	mov	waittmp,timehi
	or	waittmp,timelo
	brne	wait
	ret
	

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

;;;;;;;;;;; init hardware

	;; calibrate oscillator

	.ifdef	cal_byte
	ldi	ZL,low(cal_byte<<1)
	ldi	ZH,high(cal_byte<<1)
	lpm
	out	OSCCAL,r0
	.endif

	;; setup I/Os  (setup outputs, others are inputs)

	ldi	tmp,(( 1<<alarm )|( 1<<light )|(1<<after))
	out	DDRB,tmp	; make 'em outputs

	ldi	tmp,0xff	; should inputs be set high?
	out	PORTB,tmp	; set them high

	;; setup timer, interrupts

	ldi	tmp,ck1k
	out	TCCR0,tmp

	ldi	tmp,(1<<TOIE0)
	out	TIMSK,tmp
	ldi	tmp,(1<<TOV0)
	out	TIFR,tmp

	;; clear unused interrupts

	clr	tmp
	out	GIMSK,tmp
	out	GIFR,tmp

	;; other init

	clr	timehi
	clr	timelo
	ldi	state,st_norm

	;; enable ints

	sei

;	rcall	unitTest

;;;;;;;;;;; application main loop

	;; test initial conditions
start:
	in	tmp,pinb
	sbrs	tmp,dry
	rjmp	tripped	; skip alarm if already tripped

	;; wait for falling edge of portb.dry
watch:
	in	tmp,pinb
	sbrs	tmp,abort
	rjmp	fatal
	sbrc	tmp,dry
	rjmp	watch

	;; raise alarm for a period of time
rising:
	ldi	state,st_trip
	cbi	portb,alarm
	cbi	portb,after
	ldi	timelo,alarmtime
	rcall	wait

	;; forevermore signal that water was detected
tripped:
	ldi	state,st_trip
	sbi	portb,alarm

	in	tmp,pinb
	sbrs	tmp,abort
	rjmp	fatal
	rjmp	tripped

fatal:
	ldi	state,st_err
	rjmp	fatal

	;;NOTREACHED



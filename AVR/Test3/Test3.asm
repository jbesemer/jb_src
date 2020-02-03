;; stock example

.include "8515def.inc"

.def	Temp 	=r16
.def	Delay	=r17
.def	Delay2	=r18

;;;; vectors

	rjmp	reset


RESET:
	ser	temp
	out 	DDRB,temp

LOOP:
	out	PORTB,temp

	sbis	PIND,0x00
	inc	Temp
	sbis	PIND,0x01
	dec	Temp
	sbis	pind,2
	ror	temp
	sbis	pind,3
	rol	temp
	sbis	pind,4
	com	temp
	sbis	pind,5
	neg	temp
	sbis	pind,6
	swap	temp
	
DLY:
	dec	delay
	brne	dly
	dec	delay2
	brne	dly
	rjmp	loop

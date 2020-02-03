.include "tn12def.inc"

; TinyTv (c) 2002, Ward Cunningham
;       
;             ATtiny12
;              --v--
;    rst pb5 -|     |- vcc
;  clock pb3 -|     |- pb2 sck
;     vl pb4 -|     |- pb1 miso
;        gnd -|     |- pb0 mosi vh
;              -----        
;
;		1000
;	vl ---\/\/\/\---+-- video out
;					|
;			410		|
;	vh ---\/\/\/\---+
;
; TinyTv generates an NTSC video signal using only programmed
; output to a resistive network on portb. The timer overflow
; handler outputs horizontal sync, counts lines and fields, 
; and then dispatches directly to the next line generator
; with interrupts enabled.
; 
; Line generators alternate between in-field and vertical sync.
; Each generator sets up for the next generator before going 
; into an "infinite" loop generating video as it sees fit.


	.set vl =4			; video pins and codes
	.set vh =0  
	.set vsync =0
	.set vblack =1<<vl
	.set vgray =1<<vh
	.set vwhite =vblack+vgray 
	
	.def px2 =r1		; conic registers
	.def py2 =r2
	.def px1 =r3
	.def py1 =r4
	.def px0 =r5
	.def py0 =r6
	.def pz0 =r7
	
	.def a =r16 		; temporary variables
	.def b =r17
	

	.def tnv =r18		; interrupt variables
	.def tnv2 =r19
	.def line =r20
	.def field =r21
	.def fieldh =r22
	.def tnl =r23		; timer next line count
	.def snrl =r24		; sync next retrace
	.def snrh =r25
	
	.def vs =r26 		; register constants
	.def vb =r27
	.def vg =r28
	.def vw =r29
	.def zero =r26
	
vectors:
	rjmp reset
	rjmp reset ; external
	rjmp reset ; change
	rjmp timer
	rjmp reset ; eeprom
	rjmp reset ; compare

reset:
	ldi vs,vsync		; init constants
	ldi vb,vblack
	ldi vg,vgray
	ldi vw,vwhite
	
	out portb,vs		; start low
	out ddrb,vw	; outputs for hi
	ldi a,1<<cs01		; prescale ck/8
	out tccr0,a
	ldi a,1<<toie0		; overflow interrupt enable
	out timsk,a
;	rjmp timer
	
timer:
	out portb,tnv2	
	ldi a,-62			; hsync rate is 16 khz
	out tcnt0,a
	sei
	
	ldi a,2				; front porch
tim1:	dec a
	brne tim1
	out portb,tnv

	ldi a,13			; sync pulse
tim2:	dec a
	brne tim2
	out portb,tnv2
	
	ldi a,4				; back porch
tim3:	dec a
	brne tim3	

	dec line
	brne tim4
	ldi a,1
	add field,a
	adc fieldh,zero
	dec pz0
	mov line,tnl
tim4:	sbrs field,0	; alternate field/sync
	rjmp field
;	rjmp sync
	
	.equ retrace =0b0001110000000000
sync:
	ldi tnl,247			; setup next field
	lsl snrl
	rol snrh
	brcs syn2			; if not equilibration
	
	ldi tnv,vsync
	ldi tnv2,vblack
	out portb,vb
;	sbi portb,1			; scope sync on pb1
;	sbi ddrb,1
	rjmp syn4
	
syn2:	ldi tnv,vblack
	ldi tnv2,vsync
	out portb,vs
	
	clr py2				; conic
	inc py2 
	ldi a,-120
	mov py1,a
;	ldi a,0
	mov px0,pz0
	mov py0,pz0
	
syn4:	rjmp syn4
	
	
field:
	ldi tnv,vsync		; setup next sync
	ldi tnl,16
	ldi snrl,low(retrace)
	ldi snrh,high(retrace)
	
	sbrs fieldh,1		; alternate conic/bars/hatch
	rjmp conic
	sbrs field,7
	rjmp hatch
	rjmp bars
	
;		vert	horz	dot
;	px2	...	1	...
;	py2	1	...	...	
;
;	px1	...	-20	+py2
;	py1	-20	+py2	...
;
;	px0	0	py0	+px1
;	py0	0	+py1	...


conic:
	ldi a,8
	mov px2,a			; translate vertically
	ldi a,-40
	mov px1,a
	mov px0,py0
	mov a,py1
	asr a
	asr a
	add py0,a
	add py1,py2	

con1:
	add px1,px2			; translaate horizontally	
	add px0,px1
	brpl con2
	out portb,vg
	nop
	rjmp con1
con2:
	out portb,vw
	rjmp con1	

bars:
	out portb,vb		; black bar
	out portb,vb
	out portb,vb
	out portb,vb
	out portb,vg		; gray bar
	out portb,vg
	out portb,vg
	out portb,vg
	out portb,vw		; white bar
	out portb,vw
	rjmp bars
	
hatch:
	ldi a,7
	and a,line
	brne hat2
	
	out portb,vw		; horizontal lines
hat1:	rjmp hat1

hat2:	out portb,vw	; vertical lines
	out portb,vb
	out portb,vb
	out portb,vb
	out portb,vb
	out portb,vb
	rjmp hat2




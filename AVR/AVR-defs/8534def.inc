;***************************************************************************
;* A P P L I C A T I O N   N O T E   F O R   T H E   A V R   F A M I L Y
;* 
;* Number				:AVR000
;* File Name			:"8534def.inc"
;* Title				:Register/Bit Definitions for the AT90C8534
;* Date                 :99.01.28
;* Version              :1.30
;* Support telephone	:+47 72 88 43 88 (ATMEL Norway)
;* Support fax			:+47 72 88 43 99 (ATMEL Norway)
;* Support E-mail		:avr@atmel.com
;* Target MCU			:AT90C8534
;*
;* DESCRIPTION
;* When including this file in the assembly program file, all I/O register	
;* names and I/O register bit names appearing in the data book can be used.
;* In addition, the six registers forming the three data pointers X, Y and
;* Z have been assigned names XL - ZH. Highest RAM address for Internal 
;* SRAM is also defined 
;*
;* The Register names are represented by their hexadecimal address.
;* 
;* The Register Bit names are represented by their bit number (0-7).
;* 
;* Please observe the difference in using the bit names with instructions
;* such as "sbr"/"cbr" (set/clear bit in register) and "sbrs"/"sbrc" 
;* (skip if bit in register set/cleared). The following example illustrates
;* this:
;* 
;* in	r16,PORTB				;read PORTB latch
;* sbr	r16,(1<<PB6)+(1<<PB5)	;set PB6 and PB5 (use masks, not bit#)
;* out  PORTB,r16				;output to PORTB
;*
;* in	r16,TIFR				;read the Timer Interrupt Flag Register
;* sbrc	r16,TOV0				;test the overflow flag (use bit#)
;* rjmp	TOV0_is_set				;jump if set
;* ...							;otherwise do something else
;*
;***** Specify Device
.device AT90C8534

;***** I/O Register Definitions
.equ	SREG	=$3f
.equ	SPH		=$3e
.equ	SPL		=$3d
.equ	GIMSK	=$3b
.equ	GIFR	=$3a
.equ	TIMSK	=$39
.equ	TIFR	=$38
.equ    MCUCR   =$35
.equ	TCCR0	=$33
.equ	TCNT0	=$32
.equ	TCCR1	=$2e
.equ	TCNT1H	=$2d
.equ	TCNT1L	=$2c
.equ	EEARH	=$1f
.equ	EEARL	=$1e
.equ	EEDR	=$1d
.equ	EECR	=$1c
.equ	PORTA	=$1b
.equ	DDRA	=$1a
.equ	GIPR	=$10
.equ    ADMUX   =$07
.equ    ADCSR   =$06
.equ    ADCH    =$05
.equ    ADCL    =$04

;***** Bit Definitions
;GIMSK
.equ	INT1	=7
.equ	INT0	=6

;GIFR
.equ	INTF1	=7
.equ	INTF0	=6

;GIPR
.equ	IPIN1	=3
.equ	IPIN0	=2

;TIMSK
.equ    TOIE1   =2
.equ    TOIE0   =0

;TIFR
.equ    TOV1    =2
.equ    TOV0    =0

;MCUCR
.equ    SE      =6
.equ    SM      =5
.equ    ISC1    =2
.equ    ISC0    =0

;TCCR0
.equ	CS02	=2
.equ	CS01	=1
.equ	CS00	=0

;TCCR1
.equ	CS12	=2
.equ	CS11	=1
.equ	CS10	=0

;EECR
.equ    EERIE   =3
.equ	EEMWE	=2
.equ	EEWE	=1
.equ	EERE	=0

;PORTA
.equ	PA6	=6
.equ	PA5	=5
.equ	PA4	=4
.equ	PA3	=3
.equ	PA2	=2
.equ	PA1	=1
.equ	PA0	=0

;DDRA
.equ	DDA6	=6
.equ	DDA5	=5
.equ	DDA4	=4
.equ	DDA3	=3
.equ	DDA2	=2
.equ	DDA1	=1
.equ	DDA0	=0

;ADMUX
.equ    MUX2    =2
.equ    MUX1    =1
.equ    MUX0    =0

;ADCSR
.equ    ADEN    =7
.equ    ADSC    =6
.equ    ADFR    =5
.equ    ADIF    =4
.equ    ADIE    =3
.equ    ADPS2   =2
.equ    ADPS1   =1
.equ    ADPS0   =0

.def	XL		=r26
.def	XH		=r27
.def	YL		=r28
.def	YH		=r29
.def	ZL		=r30
.def	ZH		=r31

.equ 	RAMEND	=$15f
.equ	XRAMEND =$15F
.equ	E2END	=$1FF
.equ	FLASHEND=$FFF

.equ	INT0addr=$001	;External Interrupt0 Vector Address
.equ	INT1addr=$002	;External Interrupt1 Vector Address
.equ	OVF1addr=$003	;Overflow1 Interrupt Vector Address
.equ	OVF0addr=$004	;Overflow0 Interrupt Vector Address
.equ	ADCCaddr =$005	;ADC Interrupt Vector Address
.equ	ERDYaddr =$006	;EEPROM Interrupt Vector Address

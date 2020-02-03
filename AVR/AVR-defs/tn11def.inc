;***************************************************************************
;* A P P L I C A T I O N   N O T E   F O R   T H E   A V R   F A M I L Y
;* 
;* Number		:AVR000
;* File Name		:"tn11def.inc"
;* Title		:Register/Bit Definitions for the ATtiny11
;* Date                 :99.01.28
;* Version              :1.30
;* Support telephone	:+47 72 88 43 88 (ATMEL Norway)
;* Support fax		:+47 72 88 43 99 (ATMEL Norway)
;* Support E-mail	:avr@atmel.com
;* Target MCU		:ATtiny11
;*
;* DESCRIPTION
;* When including this file in the assembly program file, all I/O register
;* names and I/O register bit names appearing in the data book can be used.
;* In addition, the two registers forming the data pointers Z have been 
;* assigned names ZL - ZH. 
;*
;* The Register names are represented by their hexadecimal addresses.
;*
;* The Register Bit names are represented by their bit number (0-7).
;*
;* Please observe the difference in using the bit names with instructions
;* such as "sbr"/"cbr" (set/clear bit in register) and "sbrs"/"sbrc"
;* (skip if bit in register set/cleared). The following example illustrates
;* this:
;*
;* in r16,PORTB  ;read PORTB latch
;* sbr r16,(1<<PB2)+(1<<PB1) ;set PB2 and PB1 (use masks, not bit#)
;* out  PORTB,r16  ;output to PORTB
;*
;* in r16,TIFR  ;read the Timer Interrupt Flag Register
;* sbrc r16,TOV0  ;test the overflow flag (use bit#)
;* rjmp TOV0_is_set  ;jump if set
;* ...    ;otherwise do something else
;***************************************************************************



;***** Specify Device
.device ATtiny11

;***** I/O Register Definitions
.equ    SREG    =$3f
.equ    GIMSK   =$3b
.equ    GIFR    =$3a
.equ    TIMSK   =$39
.equ    TIFR    =$38
.equ    MCUCR   =$35
.equ    MCUSR   =$34
.equ    TCCR0   =$33
.equ    TCNT0   =$32
.equ    WDTCR   =$21
.equ    PORTB   =$18
.equ    DDRB    =$17
.equ    PINB    =$16
.equ    ACSR    =$08


;***** Bit Definitions

.equ    EXTRF   =1
.equ    PORF    =0

.equ    INT0    =6
.equ    PCIE    =5

.equ    INTF0   =6
.equ    PCIF    =5

.equ    TOIE0   =1

.equ    TOV0    =1

.equ    SE      =5
.equ    SM      =4
.equ    ISC01   =1
.equ    ISC00   =0

.equ    CS02    =2
.equ    CS01    =1
.equ    CS00    =0

.equ    WDTOE	=4
.equ    WDE	=3
.equ    WDP2	=2
.equ    WDP1	=1
.equ    WDP0	=0

.equ    ACD     =7
.equ    ACO     =5
.equ    ACI     =4
.equ    ACIE    =3
.equ    ACIS1   =1
.equ    ACIS0   =0

.equ    PB4     =4
.equ    PB3     =3
.equ    PB2     =2
.equ    PB1     =1
.equ    PB0     =0

.equ    DDB4    =4
.equ    DDB3    =3
.equ    DDB2    =2
.equ    DDB1    =1
.equ    DDB0    =0

.equ    PINB5   =5
.equ    PINB4   =4
.equ    PINB3   =3
.equ    PINB2   =2
.equ    PINB1   =1
.equ    PINB0   =0

.def    ZL      =R30
.def    ZH      =R31

.equ	FLASHEND=$1FF

.equ	INT0addr=$001	;External Interrupt0 Vector Address
.equ	PCINTaddr=$002	;Pin change Interrupt Vector Address
.equ	OVF0addr=$003	;Overflow0 Interrupt Vector Address
.equ	ACIaddr =$004	;Analog Comparator Interrupt Vector Address



;***************************************************************************
;* A P P L I C A T I O N   N O T E   F O R   T H E   A V R   F A M I L Y
;* 
;* Number               :AVR000
;* File Name            :"tn12.inc"
;* Title                :Register/Bit Definitions for the ATtiny12
;* Date                 :99.01.28
;* Version              :1.30
;* Support telephone    :+47 72 88 43 88 (ATMEL Norway)
;* Support fax          :+47 72 88 43 99 (ATMEL Norway)
;* Support E-mail       :avr@atmel.com
;* Target MCU           :ATtiny12
;*
;* DESCRIPTION
;* When including this file in the assembly program file, all I/O register      
;* names and I/O register bit names appearing in the data book can be used.
;* In addition, the two registers forming the data pointer Z have been 
;* assigned names ZL - ZH. 
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
;* in   r16,PORTB               ;read PORTB latch
;* sbr  r16,(1<<PB6)+(1<<PB5)   ;set PB6 and PB5 (use masks, not bit#)
;* out  PORTB,r16               ;output to PORTB
;*
;* in   r16,TIFR                ;read the Timer Interrupt Flag Register
;* sbrc r16,TOV0                ;test the overflow flag (use bit#)
;* rjmp TOV0_is_set             ;jump if set
;* ...                          ;otherwise do something else
;***************************************************************************

;***** Specify Device
.device ATtiny12

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
.equ    OSCCAL  =$31
.equ    WDTCR   =$21
.equ    EEAR    =$1e
.equ    EEDR    =$1d
.equ    EECR    =$1c
.equ    PORTB   =$18
.equ    DDRB    =$17
.equ    PINB    =$16
.equ    ACSR    =$08

;***** Bit Definitions
.equ    INT0    =6
.equ    PCIE    =5

.equ    INTF0   =6
.equ    PCIF    =5

.equ    TOIE0   =1

.equ    TOV0    =1

.equ    CS02    =2
.equ    CS01    =1
.equ    CS00    =0

.equ    PUD     =6
.equ    SE      =5
.equ    SM      =4
.equ    ISC01   =1
.equ    ISC00   =0

.equ    WDDE    =4
.equ    WDE     =3
.equ    WDP2    =2
.equ    WDP1    =1
.equ    WDP0    =0

.equ    CAL7    =7
.equ    CAL6    =6
.equ    CAL5    =5
.equ    CAL4    =4
.equ    CAL3    =3
.equ    CAL2    =2
.equ    CAL1    =1
.equ    CAL0    =0

.equ    EERIE   =3
.equ    EEMWE   =2
.equ    EEWE    =1
.equ    EERE    =0

.equ    PB4     =4
.equ    PB3     =3
.equ    PB2     =2
.equ    PB1     =1
.equ    PB0     =0

.equ    DDB5    =5
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

.equ    ACD     =7
.equ    AINBG   =6
.equ    ACO     =5
.equ    ACI     =4
.equ    ACIE    =3
.equ    ACIS1   =1
.equ    ACIS0   =0

.equ    WDRF    =3
.equ    BORF    =2
.equ    EXTRF   =1
.equ    PORF    =0

.def    ZL      =r30
.def    ZH      =r31

.equ	FLASHEND=$1FF
.equ	E2END	=$3F

.equ    INT0addr=$001   ;External Interrupt0 Vector Address
.equ    PCINTaddr=$002  ;Pin change Interrupt Vector Address
.equ    OVF0addr=$003   ;Overflow0 Interrupt Vector Address
.equ    ERDYaddr =$004  ;EEPROM Interrupt Vector Address
.equ    ACIaddr =$005   ;Analog Comparator Interrupt Vector Address


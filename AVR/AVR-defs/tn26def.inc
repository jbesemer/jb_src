;***************************************************************************
;* A P P L I C A T I O N   N O T E   F O R   T H E   A V R   F A M I L Y
;* 
;* Number				:AVR000
;* File Name			:"tiny26def.inc"
;* Title				:Register/Bit Definitions for the ATtiny26
;* Date                 :April 16th, 2002
;* Version              :1.00
;* Support telephone	:+47 72 88 87 20 (ATMEL Norway)
;* Support fax			:+47 72 88 87 18 (ATMEL Norway)
;* Support E-mail		:support@atmel.no
;* Target MCU			:ATtiny26
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
;***************************************************************************

;***** Specify Device
.device ATtiny26

;***** I/O Register Definitions
.equ	SREG	=$3F
.equ	SP		=$3D
.equ	GIMSK	=$3B
.equ	GIFR	=$3A
.equ	TIMSK	=$39
.equ	TIFR	=$38
.equ	MCUCR	=$35
.equ	MCUSR	=$34
.equ	TCCR0	=$33
.equ	TCNT0	=$32
.equ	OSCCAL	=$31
.equ	TCCR1A	=$30
.equ	TCCR1B	=$2F
.equ	TCNT1	=$2E
.equ	OCR1A	=$2D
.equ	OCR1B	=$2C
.equ	OCR1C	=$2B
.equ	PLLCSR	=$29
.equ	WDTCR	=$21
.equ	EEAR	=$1E
.equ	EEDR	=$1D
.equ	EECR	=$1C
.equ	PORTA	=$1B
.equ	DDRA	=$1A
.equ	PINA	=$19
.equ	PORTB	=$18
.equ	DDRB	=$17
.equ	PINB	=$16
.equ	USIDR	=$0F
.equ	USISR	=$0E
.equ	USICR	=$0D
.equ	ACSR	=$08
.equ	ADMUX	=$07
.equ	ADCSR	=$06
.equ	ADCH	=$05
.equ	ADCL	=$04

;***** Bit Definitions
;***** GIMSK *****
.equ	INT0	=6
.equ	PCIE1	=5
.equ	PCIE0	=4

;***** GIFR ******
.equ	INTF0	=6
.equ	PCIF	=5

;***** TIMSK *****
.equ	OCIE1A	=6
.equ	OCIE1B	=5
.equ	TOIE1	=2
.equ	TOIE0	=1

;***** TIFR ******
.equ	OCF1A	=6
.equ	OCF1B	=5
.equ	TOV1 	=2
.equ	TOV0	=1

;***** MCUCR ***** 
.equ 	PUD 	=6
.equ	SE	=5
.equ	SM1	=4
.equ	SM0	=3
.equ	ISC01	=1
.equ	ISC00	=0

;***** MCUSR ***** 
.equ	WDRF 	=3
.equ	BORF 	=2
.equ	EXTRF	=1
.equ	PORF 	=0

;***** TCCR0 *****
.equ	PSR0	=3
.equ	CS02 	=2
.equ	CS01 	=1
.equ	CS00 	=0

;***** OSCCAL ****
.equ	OSCCAL4	=4
.equ	OSCCAL3	=3
.equ	OSCCAL2	=2
.equ	OSCCAL1	=1
.equ	OSCCAL0	=0

;***** TCCR1A ****
.equ	COM1A1	=7
.equ    COM1A0	=6
.equ    COM1B1	=5
.equ    COM1B0	=4
.equ	FOC1A	=3
.equ    FOC1B   =2
.equ	PWM1A	=1
.equ	PWM1B	=0

;***** TCCR1B **** 
.equ	CTC1 	=7
.equ	PSR1 	=6
.equ	CS13 	=3
.equ	CS12 	=2
.equ	CS11 	=1
.equ	CS10 	=0

;***** PLLCSR ****
.equ	PCKE	=2
.equ	PLLE	=1
.equ	PLOCK	=0

;***** WDTCR *****
.equ	WDCE	=4
.equ	WDE		=3
.equ	WDP2	=2
.equ	WDP1	=1
.equ	WDP0	=0

;***** EEAR ******
.equ	EEAR6	=6
.equ	EEAR5	=5
.equ	EEAR4	=4
.equ	EEAR3	=3
.equ	EEAR2	=2
.equ	EEAR1	=1
.equ	EEAR0	=0

;***** EECR ******
.equ	EERIE	=3
.equ	EEMWE	=2
.equ	EEWE	=1
.equ	EERE	=0

;***** PORTA ***** 
.equ	PA7		=7
.equ	PA6		=6
.equ	PA5		=5
.equ	PA4		=4
.equ	PA3		=3
.equ	PA2		=2
.equ	PA1		=1
.equ	PA0		=0

.equ	PORTA7	=7
.equ	PORTA6	=6
.equ	PORTA5	=5
.equ	PORTA4	=4
.equ	PORTA3	=3
.equ	PORTA2	=2
.equ	PORTA1	=1
.equ	PORTA0	=0

;***** DDRA ******
.equ	DDA7	=7
.equ	DDA6	=6
.equ	DDA5	=5
.equ	DDA4	=4
.equ	DDA3	=3
.equ	DDA2	=2
.equ	DDA1	=1
.equ	DDA0	=0

;***** PINA ******
.equ	PINA7	=7
.equ	PINA6	=6
.equ	PINA5	=5
.equ	PINA4	=4
.equ	PINA3	=3
.equ	PINA2	=2
.equ	PINA1	=1
.equ	PINA0	=0

;***** PORTB ***** 
.equ	PB7		=7
.equ	PB6		=6
.equ	PB5		=5
.equ	PB4		=4
.equ	PB3		=3
.equ	PB2		=2
.equ	PB1		=1
.equ	PB0		=0

.equ	PORTB7	=7
.equ	PORTB6	=6
.equ	PORTB5	=5
.equ	PORTB4	=4
.equ	PORTB3	=3
.equ	PORTB2	=2
.equ	PORTB1	=1
.equ	PORTB0	=0

;***** DDRB ******
.equ	DDB7	=7
.equ	DDB6	=6
.equ	DDB5	=5
.equ	DDB4	=4
.equ	DDB3	=3
.equ	DDB2	=2
.equ	DDB1	=1
.equ	DDB0	=0

;***** PINB ******
.equ	PINB7	=7
.equ	PINB6	=6
.equ	PINB5	=5
.equ	PINB4	=4
.equ	PINB3	=3
.equ	PINB2	=2
.equ	PINB1	=1
.equ	PINB0	=0

;***** USISR *****
.equ	USISIF	=7
.equ	USIOIF	=6
.equ	USIPF	=5
.equ	USIDC	=4
.equ	USICNT3	=3
.equ    USICNT2 =2
.equ    USICNT1 =1
.equ    USICNT0 =0

;***** USICR *****
.equ    USISIE   =7
.equ    USIOIE  =6
.equ	USIWM1	=5
.equ	USIWM0	=4
.equ	USICS1	=3
.equ	USICS0	=2
.equ	USICLK	=1
.equ	USITC	=0

;***** ACSR ******
.equ	ACD		=7
.equ	ACBG	=6
.equ	ACO		=5
.equ	ACI		=4
.equ	ACIE	=3
.equ	ACME	=2
.equ	ACIS1	=1
.equ	ACIS0	=0

;***** ADMUX *****
.equ	REFS1	=7
.equ	REFS0	=6
.equ	ADLAR	=5
.equ	MUX4	=4
.equ	MUX3	=3
.equ	MUX2	=2
.equ	MUX1 	=1
.equ	MUX0 	=0

;***** ADCSR *****
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

.equ 	RAMEND =$DF

.equ	INT0addr	=$001	;External Interrupt0 Vector Address
.equ	IOPINSaddr	=$002	;Pin change interrupt
.equ	OC1Aaddr	=$003	;Output Compare1A Interrupt Vector Address
.equ	OC1Baddr	=$004	;Output Compare1B Interrupt Vector Address
.equ	OVF1addr	=$005	;Overflow1 Interrupt Vector Address
.equ	OVF0addr	=$006	;Overflow0 Interrupt Vector Address
.equ	USI_STARTaddr	=$007	;Universal Seria Bus Start Interrupt Address
.equ	USI_OVFaddr	=$008	;Universal Seria Bus Overflow Interrupt Address
.equ	ERDYaddr	=$009	;EEPROM Ready Interrupt Vector Address
.equ	ACIaddr 	=$00A	;Analog Comparator Interrupt Vector Address
.equ	ADCCaddr 	=$00B	;ADC conversion complete Interrupt Vector Address

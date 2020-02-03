;***************************************************************************
;* A P P L I C A T I O N   N O T E   F O R   T H E   A V R   F A M I L Y
;* 
;* Number			: AVR000
;* File Name			: "m169def.inc"
;* Title			: Register/Bit Definitions for the ATmega169
;* Date                 	: June 14th, 2001
;* Version              	: 2.0
;* Support telephone		: +47 72 88 43 88 (ATMEL Norway)
;* Support fax			: +47 72 88 43 99 (ATMEL Norway)
;* Support E-mail		: support@atmel.no
;* Target MCU			: ATmega169
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
;* in	r16,PORTB		;read PORTB latch
;* sbr	r16,(1<<PB6)+(1<<PB5)	;set PB6 and PB5 (use masks, not bit#)
;* out  PORTB,r16		;output to PORTB
;*
;* in	r16,TIFR		;read the Timer Interrupt Flag Register
;* sbrc	r16,TOV0		;test the overflow flag (use bit#)
;* rjmp	TOV0_is_set		;jump if set
;* ...				;otherwise do something else
;***************************************************************************

;**** Specify Device ****
.device ATmega169

;*****************************************************************************
; I/O Register Definitions
;*****************************************************************************

;**** Memory Mapped I/O Register Definitions  ****
.equ  LCDDR18 	= $FE
.equ  LCDDR17 	= $FD 
.equ  LCDDR16 	= $FC
.equ  LCDDR15 	= $FB
.equ  LCDDR13 	= $F9 
.equ  LCDDR12 	= $F8
.equ  LCDDR11 	= $F7
.equ  LCDDR10 	= $F6 
.equ  LCDDR8 	= $F4
.equ  LCDDR7 	= $F3
.equ  LCDDR6 	= $F2
.equ  LCDDR5 	= $F1 
.equ  LCDDR3 	= $EF
.equ  LCDDR2 	= $EE
.equ  LCDDR1 	= $ED 
.equ  LCDDR0 	= $EC
.equ  LCDCCR 	= $E7
.equ  LCDFRR 	= $E6
.equ  LCDCRB 	= $E5
.equ  LCDCRA 	= $E4
.equ  UDR0 	= $C6  
.equ  UBRR0H 	= $C5  
.equ  UBRR0L 	= $C4  
.equ  UCSR0C 	= $C2
.equ  UCSR0B 	= $C1
.equ  UCSR0A 	= $C0
.equ  USIDR	= $BA
.equ  USISR	= $B9
.equ  USICR	= $B8
.equ  ASSR 	= $B6
.equ  OCR2A	= $B3  
.equ  TCNT2 	= $B2  
.equ  TCCR2A 	= $B0
.equ  OCR1BH 	= $8B 
.equ  OCR1BL 	= $8A 
.equ  OCR1AH 	= $89 
.equ  OCR1AL 	= $88 
.equ  ICR1H 	= $87 
.equ  ICR1L 	= $86 
.equ  TCNT1H 	= $85 
.equ  TCNT1L 	= $84 
.equ  TCCR1C 	= $82 
.equ  TCCR1B 	= $81
.equ  TCCR1A 	= $80
.equ  DIDR1 	= $7F
.equ  DIDR0 	= $7E
.equ  ADMUX 	= $7C 
.equ  ADCSRB 	= $7B
.equ  ADCSRA 	= $7A
.equ  ADCH 	= $79 
.equ  ADCL 	= $78
.equ  TIMSK2 	= $70
.equ  TIMSK1 	= $6F
.equ  TIMSK0 	= $6E
.equ  PCMSK1 	= $6C
.equ  PCMSK0 	= $6B 
.equ  EICRA 	= $69 
.equ  OSCCAL 	= $66
.equ  CLKPR 	= $61
.equ  WDTCR 	= $60
.equ  SREG 	= $3F
.equ  SPH 	= $3E
.equ  SPL 	= $3D
.equ  SPMCSR 	= $37
.equ  MCUCR 	= $35
.equ  MCUSR 	= $34
.equ  SMCR 	= $33
.equ  OCDR 	= $31
.equ  ACSR 	= $30
.equ  SPDR 	= $2E 
.equ  SPSR 	= $2D
.equ  SPCR 	= $2C
.equ  GPIOR2 	= $2B 
.equ  GPIOR1 	= $2A 
.equ  OCR0A	= $27
.equ  TCNT0 	= $26 
.equ  TCCR0A 	= $24
.equ  GTCCR 	= $23
.equ  EEARH 	= $22 
.equ  EEARL 	= $21 
.equ  EEDR 	= $20
.equ  EECR 	= $1F
.equ  GPIOR0 	= $1E 
.equ  EIMSK 	= $1D
.equ  EIFR 	= $1C
.equ  TIFR2 	= $17
.equ  TIFR1 	= $16
.equ  TIFR0 	= $15
.equ  PORTG 	= $14
.equ  DDRG 	= $13
.equ  PING 	= $12
.equ  PORTF 	= $11
.equ  DDRF 	= $10
.equ  PINF 	= $0F
.equ  PORTE 	= $0E
.equ  DDRE 	= $0D
.equ  PINE 	= $0C
.equ  PORTD 	= $0B
.equ  DDRD 	= $0A
.equ  PIND 	= $09
.equ  PORTC 	= $08
.equ  DDRC 	= $07
.equ  PINC 	= $06
.equ  PORTB 	= $05
.equ  DDRB 	= $04
.equ  PINB 	= $03
.equ  PORTA 	= $02
.equ  DDRA 	= $01
.equ  PINA 	= $00

;*****************************************************************************
; Bit Definitions
;*****************************************************************************

; *** LCDDR18, LCDDR13, LCDDR8, LCDDR3 ***
.equ SEG24		= 0	

; *** LCDSR17, LCDSR12, LCDSR7, LCDSR2 ***
.equ SEG23      = 7 
.equ SEG22      = 6
.equ SEG21      = 5
.equ SEG20      = 4
.equ SEG19      = 3
.equ SEG18      = 2
.equ SEG17      = 1
.equ SEG16      = 0

; *** LCDSR16, LCDSR11, LCDSR6, LCDSR1 ***
.equ SEG15      = 7 
.equ SEG14      = 6
.equ SEG13      = 5
.equ SEG12      = 4
.equ SEG11      = 3
.equ SEG10      = 2
.equ SEG9       = 1
.equ SEG8       = 0
	
; *** LCDSR15, LCDSR10, LCDSR5, LCDSR0 ***
.equ SEG7       = 7 
.equ SEG6       = 6
.equ SEG5       = 5
.equ SEG4       = 4
.equ SEG3       = 3
.equ SEG2       = 2
.equ SEG1       = 1
.equ SEG0       = 0

; *** LCDCCR ***
.equ LCDCC3     = 3 
.equ LCDCC2     = 2
.equ LCDCC1     = 1
.equ LCDCC0     = 0

; *** LCDFRR *** 
.equ LCDPS2     = 6 
.equ LCDPS1     = 5
.equ LCDPS0     = 4
.equ LCDCD2     = 2
.equ LCDCD1     = 1
.equ LCDCD0     = 0
				
; *** LCDCRB ***
.equ LCDCS      = 7 
.equ LCDB2	= 6
.equ LCDMUX1    = 5 
.equ LCDMUX0    = 4
.equ LCDPM2     = 2
.equ LCDPM1     = 1
.equ LCDPM0     = 0
		
; *** LCDCRA ***
.equ LCDEN      = 7 
.equ LCDAB      = 6		
.equ LCDIF      = 4
.equ LCDIE      = 3
.equ LCDBL      = 0

; *** UCSR0C ***
.equ UMSEL0     = 6  
.equ UPM01      = 5
.equ UPM00      = 4
.equ USBS0      = 3
.equ UCSZ01     = 2
.equ UCSZ00     = 1
.equ UCPOL0     = 0

; *** UCSR0B ***
.equ RXCIE0     = 7  
.equ TXCIE0     = 6
.equ UDRIE0     = 5
.equ RXEN0      = 4
.equ TXEN0      = 3
.equ UCSZ02     = 2
.equ RXB80      = 1
.equ TXB80      = 0

; *** UCSR0A ***
.equ RXC0       = 7  
.equ TXC0       = 6
.equ UDRE0      = 5
.equ FE0        = 4
.equ DOR0       = 3
.equ PE0        = 2
.equ U2X0       = 1
.equ MPCM0      = 0

;*** USISR ***
.equ USISIF     = 7  
.equ USIOIF     = 6
.equ USIPF	= 5
.equ USIDC	= 4
.equ USICNT3	= 3
.equ USICNT2	= 2
.equ USICNT1	= 1
.equ USICNT0	= 0

; *** USICR ***
.equ USISIE     = 7  
.equ USIOIE     = 6
.equ USIWM1	= 5
.equ USIWM0	= 4
.equ USICS1	= 3
.equ USICS0	= 2
.equ USICLK	= 1
.equ USITC	= 0
	
; *** ASSR ***
.equ EXCLK      = 4
.equ AS2        = 3  
.equ TCN2UB     = 2
.equ OCR2UB     = 1
.equ TCR2UB     = 0

; *** TCCR2A ***
.equ FOC2       = 7  
.equ WGM20      = 6
.equ COM2A1     = 5
.equ COM2A0     = 4
.equ WGM21      = 3
.equ CS22       = 2
.equ CS21       = 1
.equ CS20       = 0

; *** TCCR1C ***
.equ FOC1A      = 7  
.equ FOC1B      = 6

; *** TCCR1B ***
.equ ICNC1      = 7  
.equ ICES1      = 6
.equ WGM13      = 4
.equ WGM12      = 3
.equ CS12       = 2
.equ CS11       = 1
.equ CS10       = 0

; *** TCCR1A ***
.equ COM1A1     = 7  
.equ COM1A0     = 6
.equ COM1B1     = 5
.equ COM1B0     = 4
.equ COM1C1     = 3
.equ COM1C0     = 2
.equ WGM11      = 1
.equ WGM10      = 0

; *** DIDR1 ***
.equ ADC7D      = 7  
.equ ADC6D      = 6
.equ ADC5D      = 5
.equ ADC4D      = 4
.equ ADC3D      = 3
.equ ADC2D      = 2
.equ ADC1D      = 1
.equ ADC0D      = 0

; *** DIDR0 ***
.equ AIN1D      = 1  
.equ AIN0D      = 0

; *** ADMUX ***
.equ REFS1      = 7  
.equ REFS0      = 6
.equ ADLAR      = 5
.equ MUX4       = 4
.equ MUX3       = 3
.equ MUX2       = 2
.equ MUX1       = 1
.equ MUX0       = 0

; *** ADCSRB ***
.equ ADHSM      = 7  
.equ ACME       = 6
.equ ADTS2      = 2
.equ ADTS1      = 1
.equ ADTS0      = 0

; *** ADCSRA ***
.equ ADEN       = 7  
.equ ADSC       = 6
.equ ADRF       = 5
.equ ADIF       = 4
.equ ADIE       = 3
.equ ADPS2      = 2
.equ ADPS1      = 1
.equ ADPS0      = 0

; *** TIMSK2 ***
.equ OCIE2A     = 1
.equ TOIE2      = 0

; *** TIMSK1 ***
.equ ICIE1      = 5  
.equ OCIE1B     = 2
.equ OCIE1A     = 1
.equ TOIE1      = 0

; *** TIMSK0 ***
.equ OCIE0A     = 1
.equ TOIE0      = 0

; *** PCMSK1 ***
.equ PCINT15    = 7  
.equ PCINT14    = 6
.equ PCINT13    = 5
.equ PCINT12    = 4
.equ PCINT11    = 3
.equ PCINT10    = 2
.equ PCINT9     = 1
.equ PCINT8     = 0

; *** PCMSK0 ***
.equ PCINT7     = 7  
.equ PCINT6     = 6
.equ PCINT5     = 5
.equ PCINT4     = 4
.equ PCINT3     = 3
.equ PCINT2     = 2
.equ PCINT1     = 1
.equ PCINT0     = 0

; *** EICRA ***
.equ ISC01	= 1
.equ ISC00	= 0

; *** CLKPR ***
.equ CLKPCE     = 7  
.equ CLKPS3     = 3
.equ CLKPS2     = 2
.equ CLKPS1     = 1
.equ CLKPS0     = 0

; *** WDTCR ***
.equ WDCE       = 4  
.equ WDE        = 3
.equ WDP2       = 2
.equ WDP1       = 1
.equ WDP0       = 0

; *** SREG ***
.equ I          = 7  
.equ T          = 6
.equ H          = 5
.equ S          = 4
.equ V          = 3
.equ N          = 2
.equ Z          = 1
.equ C          = 0

; *** SPH ***
.equ SP15       = 7  
.equ SP14       = 6
.equ SP13       = 5
.equ SP12       = 4
.equ SP11       = 3
.equ SP10       = 2
.equ SP9        = 1
.equ SP8        = 0

; *** SPL ***
.equ SP7        = 7  
.equ SP6        = 6
.equ SP5        = 5
.equ SP4        = 4
.equ SP3        = 3
.equ SP2        = 2
.equ SP1        = 1
.equ SP0        = 0

; *** SPMCSR ***
.equ SPMIE      = 7  
.equ RWWSB      = 6
.equ RWWSRE     = 4
.equ BLBSET     = 3
.equ PGWRT      = 2
.equ PGERS      = 1
.equ SPMEN      = 0

; *** MCUCR ***
.equ JTD        = 7  
.equ PUD        = 4
.equ IVSEL      = 1
.equ IVCE       = 0

; *** MCUSR ***
.equ JTRF       = 4  
.equ WDRF       = 3
.equ BORF       = 2
.equ EXTRF      = 1
.equ PORF       = 0

; *** SMCR ***
.equ SM2        = 3  
.equ SM1        = 2
.equ SM0        = 1
.equ SE         = 0

; *** OCDR ***
.equ IDRD       = 7  
.equ OCD	= 7
.equ OCDR6      = 6
.equ OCDR5      = 5
.equ OCDR4      = 4
.equ OCDR3      = 3
.equ OCDR2      = 2
.equ OCDR1      = 1
.equ OCDR0      = 0

; *** ACSR ***
.equ ACD        = 7  
.equ ACBG       = 6
.equ ACO        = 5
.equ ACI        = 4
.equ ACIE       = 3
.equ ACIC       = 2
.equ ACIS1      = 1
.equ ACIS0      = 0

; *** SPSR ***
.equ SPIF       = 7  
.equ WCOL       = 6
.equ SPI2X      = 0

; *** SPCR ***
.equ SPIE       = 7 
.equ SPE        = 6
.equ DORD       = 5
.equ MSTR       = 4
.equ CPOL       = 3
.equ CPHA       = 2
.equ SPR1       = 1
.equ SPR0       = 0

; *** TCCR0A ***
.equ FOC0A      = 7 
.equ WGM00      = 6
.equ COM0A1     = 5
.equ COM0A0     = 4
.equ WGM01      = 3
.equ CS02       = 2
.equ CS01       = 1
.equ CS00       = 0

; *** GTCCR ***
.equ TSM        = 7  
.equ PSR2       = 1
.equ PSR10      = 0
					 
; To make tim8pwm_def.inc file
; part independent.		
.equ PSR0       = PSR10	 
.equ PSR1       = PSR10
	
; *** EECR ***
.equ EERIE      = 3  
.equ EEMWE      = 2
.equ EEWE       = 1
.equ EERE       = 0

; *** EIMSK ***
.equ PCIE1      = 7
.equ PCIE0      = 6
.equ INT0       = 0

; *** EIFR ***
.equ PCIF1      = 7
.equ PCIF0      = 6
.equ INTF0      = 0

; *** TIFR2 ***
.equ OCF2A      = 1
.equ TOV2       = 0

; *** TIFR1 ***
.equ ICF1       = 5  
.equ OCF1B      = 2
.equ OCF1A      = 1
.equ TOV1       = 0

; *** TIFR0 ***
.equ OCF0A      = 1
.equ TOV0       = 0

; *** PORTG ***
.equ PORTG5     = 5
.equ PORTG4     = 4
.equ PORTG3     = 3
.equ PORTG2     = 2
.equ PORTG1     = 1
.equ PORTG0     = 0

; *** DDRG ***
.equ DDG4       = 4
.equ DDG3       = 3
.equ DDG2       = 2
.equ DDG1       = 1
.equ DDG0       = 0

; *** PING ***
.equ PING5      = 5
.equ PING4      = 4
.equ PING3      = 3
.equ PING2      = 2
.equ PING1      = 1
.equ PING0      = 0

; *** PORTF ***
.equ PORTF7     = 7  
.equ PORTF6     = 6
.equ PORTF5     = 5
.equ PORTF4     = 4
.equ PORTF3     = 3
.equ PORTF2     = 2
.equ PORTF1     = 1
.equ PORTF0     = 0

; *** DDRF ***
.equ DDF7       = 7  
.equ DDF6       = 6
.equ DDF5       = 5
.equ DDF4       = 4
.equ DDF3       = 3
.equ DDF2       = 2
.equ DDF1       = 1
.equ DDF0       = 0

; *** PINF ***
.equ PINF7      = 7  
.equ PINF6      = 6
.equ PINF5      = 5
.equ PINF4      = 4
.equ PINF3      = 3
.equ PINF2      = 2
.equ PINF1      = 1
.equ PINF0      = 0

; *** PORTE ***
.equ PORTE7     = 7  
.equ PORTE6     = 6
.equ PORTE5     = 5
.equ PORTE4     = 4
.equ PORTE3     = 3
.equ PORTE2     = 2
.equ PORTE1     = 1
.equ PORTE0     = 0

; *** DDRE ***
.equ DDE7       = 7  
.equ DDE6       = 6
.equ DDE5       = 5
.equ DDE4       = 4
.equ DDE3       = 3
.equ DDE2       = 2
.equ DDE1       = 1
.equ DDE0       = 0

; *** PINE ***
.equ PINE7      = 7  
.equ PINE6      = 6
.equ PINE5      = 5
.equ PINE4      = 4
.equ PINE3      = 3
.equ PINE2      = 2
.equ PINE1      = 1
.equ PINE0      = 0

; *** PORTD ***
.equ PORTD7     = 7  
.equ PORTD6     = 6
.equ PORTD5     = 5
.equ PORTD4     = 4
.equ PORTD3     = 3
.equ PORTD2     = 2
.equ PORTD1     = 1
.equ PORTD0     = 0

; *** DDRD ***
.equ DDD7       = 7  
.equ DDD6       = 6
.equ DDD5       = 5
.equ DDD4       = 4
.equ DDD3       = 3
.equ DDD2       = 2
.equ DDD1       = 1
.equ DDD0       = 0

; *** PIND ***
.equ PIND7      = 7  
.equ PIND6      = 6
.equ PIND5      = 5
.equ PIND4      = 4
.equ PIND3      = 3
.equ PIND2      = 2
.equ PIND1      = 1
.equ PIND0      = 0

; *** PORTC ***
.equ PORTC7     = 7  
.equ PORTC6     = 6
.equ PORTC5     = 5
.equ PORTC4     = 4
.equ PORTC3     = 3
.equ PORTC2     = 2
.equ PORTC1     = 1
.equ PORTC0     = 0

; *** DDRC ***
.equ DDC7       = 7  
.equ DDC6       = 6
.equ DDC5       = 5
.equ DDC4       = 4
.equ DDC3       = 3
.equ DDC2       = 2
.equ DDC1       = 1
.equ DDC0       = 0

; *** PINC ***
.equ PINC7      = 7  
.equ PINC6      = 6
.equ PINC5      = 5
.equ PINC4      = 4
.equ PINC3      = 3
.equ PINC2      = 2
.equ PINC1      = 1
.equ PINC0      = 0

; *** PORTB ***
.equ PORTB7     = 7  
.equ PORTB6     = 6
.equ PORTB5     = 5
.equ PORTB4     = 4
.equ PORTB3     = 3
.equ PORTB2     = 2
.equ PORTB1     = 1
.equ PORTB0     = 0

; *** DDRB ***
.equ DDB7       = 7  
.equ DDB6       = 6
.equ DDB5       = 5
.equ DDB4       = 4
.equ DDB3       = 3
.equ DDB2       = 2
.equ DDB1       = 1
.equ DDB0       = 0

; *** PINB ***
.equ PINB7      = 7  
.equ PINB6      = 6
.equ PINB5      = 5
.equ PINB4      = 4
.equ PINB3      = 3
.equ PINB2      = 2
.equ PINB1      = 1
.equ PINB0      = 0

; *** PORTA ***
.equ PORTA7     = 7  
.equ PORTA6     = 6
.equ PORTA5     = 5
.equ PORTA4     = 4
.equ PORTA3     = 3
.equ PORTA2     = 2
.equ PORTA1     = 1
.equ PORTA0     = 0

; *** DDRA ***
.equ DDA7       = 7  
.equ DDA6       = 6
.equ DDA5       = 5
.equ DDA4       = 4
.equ DDA3       = 3
.equ DDA2       = 2
.equ DDA1       = 1
.equ DDA0       = 0

; *** PINA ***
.equ PINA7      = 7  
.equ PINA6      = 6
.equ PINA5      = 5
.equ PINA4      = 4
.equ PINA3      = 3
.equ PINA2      = 2
.equ PINA1      = 1
.equ PINA0      = 0

;*****************************************************************************
; CPU Register Declarations
;*****************************************************************************

.def	XL	= r26		; X pointer low
.def	XH	= r27		; X pointer high
.def	YL	= r28		; Y pointer low
.def	YH	= r29		; Y pointer high
.def	ZL	= r30		; Z pointer low
.def	ZH	= r31		; Z pointer high


;*****************************************************************************
; Data Memory Declarations
;*****************************************************************************

.equ 	RAMEND	= $4ff		; Highest internal data memory (SRAM) address.
							;(1k RAM + IO + REG)
.equ	EEPROMEND = $01ff   ; Highest EEPROM address.
	                        ;(512 byte)
;*****************************************************************************
; Program Memory Declarations
;*****************************************************************************

.equ    FLASHEND = $1FFF	;  Highest program memory (flash) address
	                        ; (When addressed as 16 bit words)
							; ( 8k words , 16k byte ) 
		
;**** Boot Vectors ****
			;  byte groups
			;   /--\/--\/--\ 
.equ 	SMALLBOOTSTART	=0b1111110000000  ;($1F80) smallest boot block is 256B
.equ 	SECONDBOOTSTART	=0b1111100000000  ;($1F00) second boot block size is 512B
.equ 	THIRDBOOTSTART	=0b1111000000000  ;($1E00) third boot block size is 1KB
.equ 	LARGEBOOTSTART	=0b1110000000000  ;($1C00) largest boot block is 2KB
.equ 	BOOTSTART	=THIRDBOOTSTART   ;OBSOLETE!!! kept for compatibility

;**** Page Size ****
.equ	PAGESIZE	=64     ;number of WORDS in a page

;**** Interrupt Vectors ****		
.equ	INT0addr     =$002	;External Interrupt0 Interrupt Address
.equ	PCINT0addr   =$004	;Pin Change Interrupt0 Interrupt Address 
.equ	PCINT1addr   =$006	;Pin Change Interrupt1 Interrupt Address
.equ	CMP2addr     =$008 
.equ	OC2addr      =$008	;Timer/Counter2 Compare Match Interrupt Address
.equ	OVF2addr     =$00a	;Overflow1 Interrupt Address
.equ	ICP1addr     =$00c	;Input Capture1 Interrupt Address
.equ	OC1Aaddr     =$00e	;Output Compare1A Interrupt Address
.equ	OC1Baddr     =$010	;Output Compare1B Interrupt Address 
.equ	OVF1addr     =$012	;Overflow1 Interrupt Address
.equ	CMP0addr     =$014 
.equ	OC0addr      =$014	;Timer/Counter0 Compare Match Interrupt Address
.equ	OVF0addr     =$016	;Overflow0 Interrupt Address
.equ	SPIaddr      =$018	;SPI Interrupt Address
.equ	URXC0addr    =$01a	;UART Receive Complete Interrupt Address
.equ	UDRE0addr    =$01c	;UART Data Register Empty Interrupt Address
.equ	UTXC0addr    =$01e	;UART Transmit Complete Interrupt Address
.equ	USI_STARTaddr=$020	;Universal Serial Bus Start Interrupt Address   
.equ	USI_OVFaddr  =$022	;Universal Serial Bus Overflow Interrupt Address	
.equ	ACIaddr	     =$024	;Analog Comparator Interrupt Address
.equ  ADCCaddr     =$026	;ADC Conversion Complete Interrupt Address
.equ	ERDYaddr     =$028	;EEPROM write complete Interrupt Address
.equ	SPMRaddr     =$02a	;Store Program Memory Ready Interrupt Address
.equ	LCDSFaddr    =$02c	;LCD Start of Frame Interrupt Address

;for compatibility with s8515
.equ	URXCaddr=$01a	;UART Receive Complete Interrupt 
.equ	UDREaddr=$01e	;UART Data Register Empty Interrupt 
.equ	UTXCaddr=$022	;UART Transmit Complete Interrupt 


;****************************************************************************************
;* This can be included in the assembly file
;* in order to use the names in the spec sheet.
;* 
;* I/O Register Definitions per AT86RF401 spec
;****************************************************************************************

;***** device directive, will make the assembler check for illegal instructions.
.device AT86RF401

;***** I/O Register Definitions
.equ	SREG		=$3F    ; Status 
.equ	SPH     	=$3E    ; Stack Pointer High 
.equ	SPL     	=$3D    ; Stack Pointer Low 
.equ	BL_CONFIG	=$35    ; Battery Low Configuration 
.equ	B_DET   	=$34    ; Button Detect 
.equ	PWR_CTL 	=$33    ; Power Control 
.equ	IO_DATIN 	=$32    ; I/O Data In 
.equ	IO_DATOUT 	=$31    ; I/O Data Out 
.equ	IO_ENAB 	=$30    ; I/O Enable
.equ	WDTCR 	    =$22    ; Watchdog Timer Control
.equ	BTCR 		=$21    ; Bit Timer Control
.equ	BTCNT 	    =$20    ; Bit Timer Count
.equ	DEEAR	 	=$1E    ; Data EEPROM Address
.equ	DEEDR	 	=$1D    ; Data EEPROM Data
.equ	DEECR	 	=$1C    ; Data EEPROM Control
.equ	LOCKDET2 	=$17    ; Lock Detector Configuration Register 2
.equ	VCOTUNE 	=$16    ; VCO Tuning Register
.equ	PWR_ATTEN 	=$14    ; Power Attenuation Control Register
.equ	TX_CNTL	    =$12    ; Transmitter Control Register
.equ	LOCKDET1 	=$10    ; Lock Detector Configuration Register 1
.equ	SRAM_START 	=$0060	; Start of RAM
.equ	SRAM_END 	=$00DF	; End of RAM

;**** Bit Definitions
; SREG
.equ	I		=7
.equ	T		=6
.equ	H		=5
.equ	S		=4
.equ	V		=3
.equ	N		=2
.equ	Z		=1
.equ	C		=0

; BL_CONFIG
.equ	BL		=7
.equ	BLV		=6
.equ	BL5		=5
.equ	BL4		=4
.equ	BL3		=3
.equ	BL2		=2
.equ	BL1		=1
.equ	BL0		=0

; B_DET
.equ	BD5		=5
.equ	BD4		=4
.equ	BD3		=3
.equ	BD2		=2
.equ	BD1		=1
.equ	BD0		=0

; PWR_CTL
.equ	ACS2	=7
.equ	ACS1	=6
.equ	ACS0	=5
.equ	TM		=4
.equ	BD		=3
.equ	BLI		=2
.equ	SLEEP	=1
.equ	BBM		=0

; IO_DATIN
.equ	IOI5	=5
.equ	IOI4	=4
.equ	IOI3	=3
.equ	IOI2	=2
.equ	IOI1	=1
.equ	IOI0	=0

; IO_DATOUT
.equ	IOO5	=5
.equ	IOO4	=4
.equ	IOO3	=3
.equ	IOO2	=2
.equ	IOO1	=1
.equ	IOO0	=0

; IO_ENAB
.equ	BOHYST	=6
.equ	IOE5	=5
.equ	IOE4	=4
.equ	IOE3	=3
.equ	IOE2	=2
.equ	IOE1	=1
.equ	IOE0	=0

; WDTCR
.equ	WDTOE	=4
.equ	WDE		=3
.equ	WDP2	=2
.equ	WDP1	=1
.equ	WDP0	=0

; BTCR
.equ	C9		=7
.equ	C8		=6
.equ	M1		=5
.equ	M0		=4
.equ	IE		=3
.equ	F2		=2
.equ	DATA	=1
.equ	F0		=0

; BTCNT
.equ	C7		=7
.equ	C6		=6
.equ	C5		=5
.equ	C4		=4
.equ	C3		=3
.equ	C2		=2
.equ	C1		=1
.equ	C0		=0

; DEEAR
.equ	PA6		=6
.equ	PA5		=5
.equ	PA4		=4
.equ	PA3		=3
.equ	PA2		=2
.equ	PA1		=1
.equ	PA0		=0

; DEEDR
.equ	ED7		=7
.equ	ED6		=6
.equ	ED5		=5
.equ	ED4		=4
.equ	ED3		=3
.equ	ED2		=2
.equ	ED1		=1
.equ	ED0		=0

; DEECR
.equ	BSY		=3
.equ	EEU		=2
.equ	EEL		=1
.equ	EER		=0

; LOCKDET2
.equ	EUD		=7
.equ	LAT		=6
.equ	ULC2	=5
.equ	ULC1	=4
.equ	ULC0	=3
.equ	LC2		=2
.equ	LC1		=1
.equ	LC0		=0

; VCOTUNE
.equ	VCOVDET1	=7
.equ	VCOVDET0	=6
.equ	VCOTUNE4	=4
.equ	VCOTUNE3	=3
.equ	VCOTUNE2	=2
.equ	VCOTUNE1	=1
.equ	VCOTUNE0	=0

; PWR_ATTEN
.equ	PCC2	=5
.equ	PCC1	=4
.equ	PCC0	=3
.equ	PCF2	=2
.equ	PCF1	=1
.equ	PCF0	=0

; TX_CNTL
.equ	FSK		=6
.equ	TXE		=5
.equ	TXK		=4
.equ	LOC		=2

; LOCKDET1
.equ	UPOK	=4
.equ	ENKO	=3
.equ	BOD		=2
.equ	CS1		=1
.equ	CS0		=0

;****************************************************************************************
;* Define global registers
;****************************************************************************************

.def         XL      =R26   
.def         XH      =R27   
.def         YL      =R28   
.def         YH      =R29   
.def         ZL      =R30   
.def         ZH      =R31   

///////////////////////////////////////
// 6 byte arithmetic for hi-res timers
///////////////////////////////////////

// 48 bit signed/unsigned add: xx += yy

useix void 
add66( void* xx, void* yy )
{
#asm
	ld		l,(ix+xx)
	ld		h,(ix+xx+1)
	ld		e,(ix+yy)
	ld		d,(ix+yy+1)
	ld		b,6
	XOR		a
loop:
	ld		a,(de)
	adc		a,(hl)
	ld		(hl),a
	inc		hl
	inc		de
	djnz	loop
#endasm
}

// 48 bit subtract: xx -= yy

useix void 
sub66( void* xx, void* yy )
{
#asm
	ld		l,(ix+yy)
	ld		h,(ix+yy+1)
	ld		e,(ix+xx)
	ld		d,(ix+yy+1)
	ld		b,6
	XOR		a
loop:
	ld		a,(de)
	sbc		a,(hl)
	ld		(de),a
	inc		hl
	inc		de
	djnz	loop
#endasm
}

// add 16 bit signed quantity to 48 bit string

useix void
add62( void* xx, word yy )
{
#asm
	ld		l,(ix+xx)
	ld		h,(ix+xx+1)
	ld		e,(ix+yy)
	ld		d,(ix+yy+1)

	// add 1st 2 bytes

	ld		a,(hl)
	add		a,e
	ld		(hl),a
	inc		hl

	ld		a,(hl)
	adc		a,d
	ld		(hl),a
	inc		hl

	// set d to 0 or FF depending on sign of d

	push	af
	bit		7,d
	jr		nz,aa
	ld		d,0
	jr		bb
aa:
	ld		d,0xFF
bb:
	pop		af

	// propigate carry to remaing 4 bytes

	ld		b,4
loop:
	ld		a,(hl)
	adc		a,c
	ld		(hl),a
	inc		hl
	djnz	loop
#endasm
}

// add 8 bit signed quantity to 48 bit string

useix void
add61( void* xx, byte yy )
{
#asm
	ld		l,(ix+xx)
	ld		h,(ix+xx+1)
	ld		e,(ix+yy)

	add		a,e
	push	af
	bit		7,e
	jr		nz,aa
	ld		d,0
	jr		bb
aa:
	ld		d,0xFF
bb:
	pop		af

	ld		b,5
loop:
	ld		a,(hl)
	adc		a,e
	ld		(hl),a
	inc		hl
	djnz	loop
#endasm
}

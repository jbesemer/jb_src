#! env python

import os, os.path

PREFIX = "\33["

def EraseScreen():				return PREFIX + "2J" 
def EraseLine():				return PREFIX + "K" 

def CursorPos(line,column):		return (PREFIX + "%d;%dH") % (line,column)
def CursorPos(line,column):		return (PREFIX + "%d;%df") % (line,column)

def CursorUp( n ):				return (PREFIX + "%dA") % n
def CursorDown( n ):			return (PREFIX + "%dB") % n
def CursorRight( n ):			return (PREFIX + "%dA") % n
def CursorLeft( n ):			return (PREFIX + "%dB") % n

def CursorSave():				return PREFIX + "s"
def CursorRestore():			return PREFIX + "u"

def SetAttr(*attr):				return PREFIX + ";".join( attr ) + "m"

			# Text attributes

ALL_OFF 	= 0    # All attributes off
BOLD 		= 1    # Bold on
UNDERLINE	= 4    # Underscore (on monochrome display adapter only)
BLINK 		= 5    # Blink on
REVERSE		= 7    # Reverse video on
CONCEALED	= 8    # Concealed on

			# Foreground colors

FG_BLACK	= 30    # Black
FG_RED      = 31    # Red
FG_GREEN    = 32    # Green
FG_YELLOW   = 33    # Yellow
FG_BLUE     = 34    # Blue
FG_MAGENTA  = 35    # Magenta
CFG_YAN     = 36    # Cyan
FG_WHITE    = 37    # White

			# Background colors

BG_BLACK	= 40    # Black
BG_RED      = 41    # Red
BG_GREEN    = 42    # Green
BG_YELLOW   = 43    # Yellow
BG_BLUE     = 44    # Blue
BG_MAGENTA  = 45    # Magenta
BG_CYAN     = 46    # Cyan
BG_WHITE    = 47    # White


cd "C:\Documents and Settings\jbesemer\Application Data\AVR Projects\vid\"
C:
del vid.map
del vid.lst
"C:\Program Files\Atmel\AVR Tools\AvrAssembler\avrasm32.exe" -fI "C:\Documents and Settings\jbesemer\Application Data\AVR Projects\vid\vid.asm" -o "vid.hex" -d "vid.obj" -e "vid.eep" -I "C:\Documents and Settings\jbesemer\Application Data\AVR Projects\vid" -I "C:\Program Files\Atmel\AVR Tools\AvrAssembler\AppNotes" -w  -m "vid.map"

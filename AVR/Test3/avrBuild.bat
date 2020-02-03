cd "C:\Documents and Settings\jb\My Documents\Test3\"
C:
del test3.map
del test3.lst
"C:\Program Files\Atmel\AVR Tools\AvrAssembler\avrasm32.exe" -fI "C:\Documents and Settings\jb\My Documents\Test3\Test3.asm" -o "test3.hex" -d "test3.obj" -e "test3.eep" -I "C:\Documents and Settings\jb\My Documents\Test3" -I "C:\Program Files\Atmel\AVR Tools\AvrAssembler\AppNotes" -w  -m "test3.map"

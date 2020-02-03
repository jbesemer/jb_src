cd "C:\Documents and Settings\jb\My Documents\Test2\"
C:
del test2.map
del test2.lst
"C:\Program Files\Atmel\AVR Tools\AvrAssembler\avrasm32.exe" -fI "C:\Documents and Settings\jb\My Documents\Test2\Test2.asm" -o "test2.hex" -d "test2.obj" -e "test2.eep" -I "C:\Documents and Settings\jb\My Documents\Test2" -I "C:\Program Files\Atmel\AVR Tools\AvrAssembler\AppNotes" -w  -m "test2.map"

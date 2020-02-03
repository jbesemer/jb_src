cd "C:\Documents and Settings\jb\My Documents\Test1\"
C:
del "C:\Documents and Settings\jb\My Documents\Test1\test1.map"
del "C:\Documents and Settings\jb\My Documents\Test1\test1.lst"
"C:\Program Files\Atmel\AVR Tools\AvrAssembler\avrasm32.exe" -fI "C:\Documents and Settings\jb\My Documents\Test1\Test1.asm" -o "C:\Documents and Settings\jb\My Documents\Test1\test1.hex" -d "C:\Documents and Settings\jb\My Documents\Test1\test1.obj" -e "C:\Documents and Settings\jb\My Documents\Test1\test1.eep" -I "C:\Documents and Settings\jb\My Documents\Test1" -I "C:\Program Files\Atmel\AVR Tools\AvrAssembler\AppNotes" -w  -m "C:\Documents and Settings\jb\My Documents\Test1\test1.map"

cd "C:\Documents and Settings\jb\My Documents\Bugger\"
C:
del "C:\Documents and Settings\jb\My Documents\Bugger\bugger.map"
del "C:\Documents and Settings\jb\My Documents\Bugger\bugger.lst"
"C:\Program Files\Atmel\AVR Tools\AvrAssembler\avrasm32.exe" -fI "C:\Documents and Settings\jb\My Documents\Bugger\Main.asm" -o "C:\Documents and Settings\jb\My Documents\Bugger\bugger.hex" -d "C:\Documents and Settings\jb\My Documents\Bugger\bugger.obj" -e "C:\Documents and Settings\jb\My Documents\Bugger\bugger.eep" -I "C:\Documents and Settings\jb\My Documents\Bugger" -I "C:\Program Files\Atmel\AVR Tools\AvrAssembler\AppNotes" -w  -m "C:\Documents and Settings\jb\My Documents\Bugger\bugger.map"

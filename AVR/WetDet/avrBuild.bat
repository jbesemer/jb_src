@ECHO OFF
"C:\Program Files\Atmel\AVR Tools\AvrAssembler2\avrasm2.exe" -S "C:\Usr\src\AVR\WetDet\labels.tmp" -fI -W+ie -o "C:\Usr\src\AVR\WetDet\WetDet.hex" -d "C:\Usr\src\AVR\WetDet\WetDet.obj" -e "C:\Usr\src\AVR\WetDet\WetDet.eep" -m "C:\Usr\src\AVR\WetDet\WetDet.map" "C:\Usr\src\AVR\WetDet\WetDet.asm"

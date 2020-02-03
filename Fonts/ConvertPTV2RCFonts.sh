#! bash

DIR=PTV_System_Fonts
for f in 9 12 16
do
	python DumpFont.py ${DIR}/SysFontStyle$f.bft > ${DIR}/SysFontStyle$f.txt
	python PTV2RCFont.py ${DIR}/SysFontStyle$f.bft
done

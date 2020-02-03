DIR=PTV_System_Fonts
for f in 9 12 16
do
	python PTVFontFile.py ${DIR}/SysFontStyle$f.bft >${DIR}/SysFontStyle$f.txt
done

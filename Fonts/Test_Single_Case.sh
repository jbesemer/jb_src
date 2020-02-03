#! env bash

for SRC in $*
do
	DIR=`dirname $SRC`
	BASE=$DIR/`basename $SRC .bft`

	python DumpFont.py $SRC > $BASE.txt
	python DumpFont.py -xa -m=8 -rm=0 $SRC > $BASE-converted.txt		# -xm 
	python PTV2RCFont.py $SRC
	echo ""
	
done


exit 0

#!/usr/bin/python2.1

import time, os
from playtime import *

def getDelta():
	interval = 15

	t = time.localtime()
	mi = t[4]
	delta = ( interval - ( mi % interval )) * 60 - t[5]
#	print "%02d:%02d" % ( t[3], t[4]), "->", delta
	return delta 

while 1:
	playtime()
	time.sleep( getDelta())


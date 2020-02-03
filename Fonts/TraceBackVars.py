
import time
import os
import sys
import StringIO
import traceback

import StringIO
import traceback

def TraceBackVars( excinfo=None, lastframes=8 ):
	if excinfo is None:
		excinfo=sys.exc_info()

	traceback.print_exception(*excinfo )
	tb=excinfo[2]
	
	while True:
		if not tb.tb_next:
			break
		tb=tb.tb_next
	stack=[]
	f=tb.tb_frame
	while f:
		stack.append(f)
		f=f.f_back
		
	stack.reverse()
	if len(stack)>lastframes:
		stack=stack[-lastframes:]
			
	print "\nVariables by last %d frames, innermost last" % (lastframes,)
	for frame in stack:
		print ""
		print "Frame %s in %s at line %s" \
				% ( frame.f_code.co_name,
					 frame.f_code.co_filename,
					 frame.f_lineno)

		for key,value in frame.f_locals.items():
			# filter out modules
			if type(value)==type(sys):
				continue
			print "%15s = " % (key,),
			try:
				print `value`[:160]
			except:
				print "(Exception occurred printing value)"

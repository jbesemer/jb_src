from __future__ import generators

########################################
# generators to parse and return whole lines from
# input sources such as sockets or files on serial ports
# which do not properly implement .readline().
#
# Usage:
#
#	self.getline = gen_sock_getline( self.sock )
#	...
#	for line in self.getline: ...
#

def gen_sock_getline( sock ):

	"""	generator to deliver successive whole lines 
		of text from an open socket.  In this context,
		a "socket" is any object implementing .recv().
	"""

	pending = ""

	while 1:
		data = sock.recv( 666 )
		if not data:
			return	# signal eof
		pending += data

		# only whole lines constitute a command

		while '\n' in pending:
			line, pending = pending.split( "\n", 1 )
			yield line


def gen_file_getline( file ):

	"""	generator to deliver successive whole lines 
		of text from an open file (e.g., a tty, which
		might not complete read in terms of entire 
		lines.  In this context, a "file" is any 
		object implementing .read().
	"""
	
	pending = ""

	while 1:
		data = file.read( 666 )
		if not data:
			return	# signal eof
		pending += data

		# only whole lines constitute a command

		while '\n' in pending:
			line, pending = pending.split( "\n", 1 )
			yield line


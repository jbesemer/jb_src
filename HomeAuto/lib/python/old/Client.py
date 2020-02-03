class Client:
	def __init__( self, sock, addr=None ):
		self.sock = sock
		self.addr = addr
		self.name = "unk"

	def put( self, data ):
		self.sock.send( data )

	def getline( self ):
		pending = ""
		while 1:
			data = self.sock.recv( 666 )
			if not data:
				return
			pending += data

			# only whole lines constitute a command

			while '\n' in pending:
				pos = pending.index( '\n' )
				cmd = pending[ : pos ]
				pending = pending[ pos+1 : ]
				if ECHOFLAG:
					print "# get:", cmd
				yield cmd

	def setname( self, name="" ):
		self.name = name
		print "# New Client:", name

	def Main( self ):
		self.start()

		commands = self.getline()
		for cmd in commands:
			self.Dispatch( cmd )

		self.exit()

	def Reply( self, response=None ):
		if response <> None:
			self.put( response )
		self.put( "\n#Done\n" )

	def Error( self, message="" ):
		self.put( "\n#Error -- " + message + "\n" )



import SocketServer
import threads
import socket

HOST=""
PORT=50010

MyServer = class( SocketServer.ThreadingTCPServer ):

	def process_request( self, request, client_address ):
		peer = request.getpeername()
		while 1:
			data = request.recv( 100 )
			print peer+":", data
		self.finish_request( request, client_address )
		self.close_request( request )

server = MyServer((HOST,PORT),  )
server.serve_forever()


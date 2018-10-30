import random, sys, socket
from time import sleep
from _thread import start_new_thread


# TODO: write generic socket tools
class FrontendSocket:
	def __init__(self, address, handler):
		self.address = address
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.handler = handler

	def _socket_receive(self, sock):
		while True:
			data = sock.recv(1024)
			if not data: raise ConnectionError('Broken pipe, no more data received')
			self.handler(data.decode('utf-8').strip())

	def connect_frontend(self):
		try:
			self.sock.bind(self.address)
			self.sock.listen(1)
			print('TCP server listening to frontend at %s %s' % self.address)
			conn, addr = self.sock.accept()
			start_new_thread(self._socket_receive, (conn,))
			while True:
				conn.send(str(random.random()).encode('utf-8'))
				sleep(0.2)
		except socket.error as e:
			sys.stderr.write('Connection failed: %s\n' % str(e))
		except Exception as e:
			sys.stderr.write('Exception: %s\n' % str(e))
		finally:
			self.sock.close()
			print('Frontend socket closed')

	def run(self):
		start_new_thread(self.connect_frontend, ())



import socket, sys


def udp_server(udp_sock, address):
	try:
		print('Binding..')
		udp_sock.bind(address)
		print('UDP: Listening to %s %s' % address)
		while True:
			data, addr = udp_sock.recvfrom(1024)
			print(data.hex().upper())
	except socket.error as e:
		sys.stderr.write('Socket Error: %s\n' % str(e))
	except Exception as e:
		sys.stderr.write('Error: %s\n' % str(e))
	finally:
		sock.close()
		print('Socket closed')
		sys.exit(0)


class UDPClient:
	def __init__(self, host, port):
		self.address = (host, port)
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	def send(self, message):
		self.sock.sendto(message, self.address)

	def read(self):
		while True:
			data = self.sock.recv(1024)
			yield data


class TCPServer:
	'''
	Accepts only one connection
	'''
	def __init__(self, host, port):
		self.address = (host, port)
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		print('TCP server listening to frontend at %s %s' % self.address)
		self.sock.bind(self.address)
		self.sock.listen(1)
		self.conn, self.addr = self.sock.accept()

	def send(self, message):
		self.conn.send(message.encode('utf-8'))

	def read(self):
		while True:
			data = self.conn.recv(1024)
			if not data: raise ConnectionError('Broken pipe, no more data received')
			yield data

	def close(self):
		self.sock.close()
		print('TCP Server closed.')


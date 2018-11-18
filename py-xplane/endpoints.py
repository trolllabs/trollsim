import socket, sys, serial, threading
from _thread import start_new_thread


class UDPClient:
	def __init__(self, host, port):
		self.lock = threading.Lock()
		self.address = (host, port)
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	def send(self, message):
		with self.lock:
			self.sock.sendto(message, self.address)

	def read(self):
		while True:
			data = self.sock.recv(1024)
			yield data


class UDPServer:
	def __init__(self, host, port):
		self.lock = threading.Lock()
		self.address = (host, port)
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		print('UDP server listening at %s %s' % self.address)
		self.sock.bind(self.address)

	def send(self, message, addr):
		with self.lock:
			self.sock.sendto(message, addr)

	def read(self):
		while True:
			data, addr = self.sock.recvfrom(509)
			yield data


class TCPServer:
	'''
	Accepts only one connection
	'''
	def __init__(self, host, port):
		self.lock = threading.Lock()
		self.address = (host, port)
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		print('TCP server listening to frontend at %s %s' % self.address)
		self.sock.bind(self.address)
		self.sock.listen(1)
		self.conn, self.addr = self.sock.accept()

	def send(self, message):
		with self.lock:
			self.conn.send(message)

	def read(self):
		while True:
			data = self.conn.recv(1024)
			if not data: raise ConnectionError('Broken pipe, no more data received')
			yield data

	def close(self):
		self.sock.close()
		print('TCP Server closed.')


class Arduino:
	def __init__(self, serial_number, baudrate):
		from serial.tools import list_ports
		self.lock = threading.Lock()
		try:
			print('Looking up arduino with serial number %s..' % serial_number)
			arduino_port = next(list_ports.grep(serial_number))
			print('Found hwid: %s' % arduino_port.hwid)
			self.serial_io = serial.Serial(arduino_port.device, baudrate)
		except StopIteration:
			sys.stderr.write('Arduino: Could not find serial number. Is it correct?\n')
			raise Exception # Crash and burn for now
		except serial.serialutil.SerialExcepion as e:
			error_msg = 'Arduino error: %s\n' % str(e)
			sys.stderr.write(error_msg)
			logging.exception(error_msg)
			raise Exception # Crash and burn for now

	def send(self, message):
		with self.lock:
			#serial_message = struct.pack()
			#self.serial_io.write(message.encode('utf-8'))
			pass # REWRITE

	def read(self):
		while True:
			try:
				reading = self.serial_io.readline()
				if reading:
					yield reading
			except UnicodeDecodeError as e:
				sys.stderr.write('Decode error at Arduino: %s\n' % str(e))


class ObservableData:
	def __init__(self, callback_reader):
		self.listeners = []
		self.reader = callback_reader

	def add_listener(self, listener):
		self.listeners.append(listener)

	def _notify_listeners(self, message):
		for listener in self.listeners:
			listener(message)

	def _run(self):
		for data in self.reader():
			self._notify_listeners(data)

	def __call__(self):
		start_new_thread(self._run, ())


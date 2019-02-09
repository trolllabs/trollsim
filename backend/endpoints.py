import socket, sys, serial, threading, struct
from serial.tools import list_ports


''' Endpoints

This module contains all the endpoint logic. Most classes here should
have standardized read and send methods, unless they are intended for
only one way communication.

The read method is intended to be a private method as all external read
calls should go through observer subscription pattern.
'''


class ObservableReading:
	'''
	Implementation of the observer pattern through callbacks. External
	functions can read children classes through a callback handler with
	add_listener(callback)
	'''
	def __init__(self):
		self.listeners = []
		self.lock = threading.Lock()

	def add_listener(self, listener):
		self.listeners.append(listener)

	def _notify_listeners(self, message):
		for listener in self.listeners:
			listener(message)

	def _read(self):
		'''
		Force _read implementation for children classes
		'''
		raise NotImplementedError('ObservableReading: No read function implemented!')

	def __call__(self):
		thread = threading.Thread(target=self._read, args=())
		thread.start()
		return thread


class UDPClient(ObservableReading):
	'''
	Args:
		config (dict): Has the keywords "id", "ip" and "port" to
			establish a connection to socket server.
			The "id" keyword is the packet identifier for where a
			reading originates from.
	'''
	def __init__(self, config):
		ObservableReading.__init__(self)
		self.address = (config['ip'], config['port'])
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	def send(self, message):
		with self.lock:
			self.sock.sendto(message, self.address)

	def _read(self):
		while True:
			data = self.sock.recv(1024)
			self._notify_listeners(data)


class UDPServer(ObservableReading):
	'''
	Args:
		config (dict): Has the keywords "id", "ip" and "port" to
			establish a socket server.
			The "id" keyword is the packet identifier for where a
			reading originates from.
	'''
	def __init__(self, config):
		ObservableReading.__init__(self)
		self.address = (config['ip'], config['port'])
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		print('UDP server listening at %s %s' % self.address)
		self.sock.bind(self.address)

	def send(self, message, addr):
		with self.lock:
			self.sock.sendto(message, addr)

	def _read(self):
		while True:
			data, addr = self.sock.recvfrom(509)
			self._notify_listeners(data)


class TCPServer(ObservableReading):
	'''
	Accepts only one connection.

	Args:
		config (dict): Has the keywords "id", "ip" and "port" to
			establish a socket server.
			The "id" keyword is the packet identifier for where a
			reading originates from.
	'''
	def __init__(self, config):
		ObservableReading.__init__(self)
		self.address = (config['ip'], config['port'])
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		print('TCP server listening to frontend at %s %s' % self.address)
		self.sock.bind(self.address)
		self.sock.listen(1)
		self.conn, self.addr = self.sock.accept()

	def send(self, message):
		with self.lock:
			self.conn.send(message)

	def _read(self):
		while True:
			data = self.conn.recv(1024)
			if not data: raise ConnectionError('Broken pipe, no more data received')
			self._notify_listeners(data)

	def close(self):
		self.sock.close()
		print('TCP Server closed.')


class Arduino(ObservableReading):
	'''
	Args:
		config (dict): Has the keywords "id", "sn" and "baudrate" to
			establish connection with a specific arduino.
			The "id" keyword is the packet identifier for where a
			reading originates from.
			"sn" stands for serial number, which are unique for all
			arduinos.
	'''
	def __init__(self, config):
		ObservableReading.__init__(self)
		try:
			print('Arduino: Looking up %s..' % config['name'])
			arduino_port = next(list_ports.grep(config['sn']))
			print('%s: Found hwid: %s at %s' \
					% (config['name'], arduino_port.hwid, arduino_port.device))
			self.serial_io = serial.Serial(arduino_port.device, config['baudrate'])
		except StopIteration:
			e = 'Arduino: Could not find serial %s for %s.\n' % (config['sn'], config['name'])
			sys.stderr.write(e)
		except serial.serialutil.SerialExcepion as e:
			e = 'Arduino error: %s\n' % str(e)
			sys.stderr.write(e)
			logging.exception(e)
			raise Exception # Crash and burn for now

	def send(self, message):
		with self.lock:
			try:
				serial_message = struct.pack('>i', message)
				self.serial_io.write(serial_message)
			except Exception as e:
				logging.exception(e)

	def _read(self):
		while True:
			try:
				reading = self.serial_io.readline()
				if reading:
					self._notify_listeners(reading)
			except UnicodeDecodeError as e:
				sys.stderr.write('Decode error at Arduino: %s\n' % str(e))


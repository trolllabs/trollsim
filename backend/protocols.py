import socket, sys, serial, threading, struct
from serial.tools import list_ports
from misc import TrollPacket, Observable


''' Endpoints

This module contains all the endpoint logic. Most classes here should
have standardized read and send methods, unless they are intended for
only one way communication.

The read method is intended to be a private method as all external read
calls should go through observer subscription pattern.
'''


class ObservableReading(Observable):
	def _read(self):
		'''
		Force _read implementation for children classes
		'''
		raise NotImplementedError('ObservableReading: No read function implemented!')


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


class Serial(ObservableReading):
	'''
	Args:
		config (dict): Has the keywords "id", "sn" and "baudrate" to
			establish connection with a specific serial unit.
			The "id" keyword is the packet identifier for where a
			reading originates from.
			"sn" stands for serial number, which are unique for all
			serial units.
	'''
	def __init__(self, config):
		ObservableReading.__init__(self)
		try:
			print('Serial: Looking up %s..' % config['name'])
			serial_port = next(list_ports.grep(config['sn']))
			print('%s: Found hwid: %s at %s' \
					% (config['name'], serial_port.hwid, serial_port.device))
			self.serial_io = serial.Serial(serial_port.device, config['baudrate'])
		except StopIteration:
			e = 'Serial: Could not find serial %s for %s.\n' % (config['sn'], config['name'])
			sys.stderr.write(e)
		except serial.serialutil.SerialExcepion as e:
			e = 'Serial error: %s\n' % str(e)
			sys.stderr.write(e)
			logging.exception(e)
			raise Exception # Crash and burn for now

	def send(self, message):
		with self.lock:
			self.serial_io.write(message)

	def _read(self):
		while True:
			reading = self.serial_io.readline()
			self._notify_listeners(reading[:-1]) # remove newline character

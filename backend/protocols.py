import socket, sys, serial, threading, struct, bluetooth
from serial.tools import list_ports
from datastructures import TrollPacket
from patterns import Observable
from time import sleep


''' Endpoints

This module contains all the endpoint logic. Most classes here should
have standardized read and send methods, unless they are intended for
only one way communication.

The read method is intended to be a private method as all external read
calls should go through observer subscription pattern.
'''


class ObservableReading(Observable):
	'''
	Force method implementation for children classes
	'''
	def connect(self):
		raise NotImplementedError('ObservableReading: No connect function implemented!')

	def send(self):
		raise NotImplementedError('ObservableReading: No send function implemented!')

	def read(self):
		raise NotImplementedError('ObservableReading: No read function implemented!')

	def close(self):
		raise NotImplementedError('ObservableReading: No close function implemented!')


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
		self.config = config
		self.address = (self.config['ip'], self.config['port'])
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	def connect(self):
		pass # Does not need to

	def send(self, message):
		with self.lock:
			self.sock.sendto(message, self.address)

	def read(self):
		data = self.sock.recv(self.config['buffer-size'])
		self._notify_listeners(data)

	def close(self):
		self.sock.close()
		print('UDPClient with address %s:%s closed' % self.address)


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
		self.config = config
		self.address = (self.config['ip'], self.config['port'])
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind((config['ip'], config['port']))
		print('UDP server listening at %s %s' % (config['ip'], config['port']))

	def connect(self):
		pass # Does not need to

	def send(self, message):
		with self.lock:
			self.sock.sendto(message, self.address)

	def read(self):
		data, addr = self.sock.recvfrom(self.config['buffer-size'])
		self._notify_listeners(data)

	def close(self):
		self.sock.close()
		print('UDPServer with address %s:%s closed' % self.address)


class TCPClient(ObservableReading):
	def __init__(self, config):
		ObservableReading.__init__(self)
		self.config = config
		self.address = (config['ip'], config['port'])
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	def connect(self):
		self.sock.connect(self.address)

	def send(self, message):
		with self.lock:
			self.sock.send(message)

	def read(self):
		data = self.sock.recv(self.config['buffer-size'])
		if not data: raise ConnectionError('Broken pipe, no more data received')
		self._notify_listeners(data)

	def close(self):
		self.sock.close()
		print('TCP Server closed.')


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
		self.config = config
		self.address = (config['ip'], config['port'])
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		print('TCP server listening to %s %s' % self.address)
		self.sock.bind(self.address)
		self.sock.listen(1)

	def connect(self):
		self.conn, self.addr = self.sock.accept()
		print('TCPServer: new connection', self.addr)

	def send(self, message):
		with self.lock:
			self.conn.send(message)

	def read(self):
		data = self.conn.recv(self.config['buffer-size'])
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
		self.config = config

	def connect(self):
		while True:
			try:
				print('Serial: Looking up %s..' % self.config['name'])
				serial_port = next(list_ports.grep(self.config['sn']))
				print('%s: Found hwid: %s at %s' \
						% (self.config['name'], serial_port.hwid, serial_port.device))
				self.serial_io = serial.Serial(serial_port.device, self.config['baudrate'])
				return
			except StopIteration:
				e = 'Serial: Could not find serial %s for %s.\n' % (self.config['sn'], self.config['name'])
				sys.stderr.write(e)
			except serial.serialutil.SerialExcepion as e:
				e = 'Serial error: %s\n' % str(e)
				sys.stderr.write(e)
				logging.exception(e)
				raise Exception # Crash and burn for now
			print('Could not establish connection. Retrying.')
			sleep(3)

	def send(self, message):
		with self.lock:
			self.serial_io.write(message)

	def read(self):
		reading = self.serial_io.readline()
		self._notify_listeners(reading[:-1]) # remove newline character

	def close(self):
		self.serial_io.close()
		print('Serial %s closed'% self.config['sn'])


class Bluetooth(ObservableReading):
	def __init__(self, config):
		ObservableReading.__init__(self)
		self.config = config
		self.bt_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

	def connect(self):
		while True:
			try:
				print('Bluetooth: Connecting to %s..' % self.config['name'])
				self.bt_sock.connect((self.config['mac'], 1))
				return
			except bluetooth.BluetoothError as e:
				print('Bluetooth error: ', e)
				print('Retrying')
			sleep(2)

	def send(self, message):
		with self.lock:
			self.bt_sock.send(message)

	def read(self):
		reading = self.bt_sock.recv(self.config['buffer-size'])
		self._notify_listeners(reading)


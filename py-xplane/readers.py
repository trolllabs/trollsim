import sys, serial, logging
from _thread import start_new_thread


class ArduinoReader:
	def __init__(self, arduino_ports, baudrate):
		self.baudrate = baudrate
		self.arduino_ports = arduino_ports
		self.listeners = []

	def add_listener(self, listener):
		self.listeners.append(listener)

	def _notify_listeners(self, message):
		for listener in self.listeners:
			listener(message)

	def _run(self):
		for port in self.arduino_ports:
			try:
				print('Trying %s..' % port)
				self.arduino_unit = serial.Serial(port, self.baudrate)
				print('starting to read from %s' % port)
				while True:
					try:
						reading = self.arduino_unit.readline().decode('utf-8')
						if reading:
							self._notify_listeners(reading)
					except UnicodeDecodeError as e:
						sys.stderr.write('Decode error at ArduinoReader: %s\n' % str(e))
			except serial.serialutil.SerialException as e:
				sys.stderr.write('ArduinoReader error: %s\n' % str(e))
				logging.exception('ArduinoReader: Did not find port %s\n' % port)
		raise ConnectionError('Could not find arduino on specified ports: %s' % self.arduino_ports)

	def __call__(self):
		start_new_thread(self._run, ())


class SocketReader:
	def __init__(self, socket_read):
		self.listeners = []
		self.reader = socket_read

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


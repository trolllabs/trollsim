import sys, serial, logging


class ArduinoReader:
	def __init__(self, arduino_ports, baudrate):
		self.baudrate = baudrate
		self.arduino_ports = arduino_ports

	def _read_arduino(self):
		for port in self.arduino_ports:
			try:
				print('Trying %s..' % port)
				self.arduino_unit = serial.Serial(port, self.baudrate)
				while True:
					try:
						reading = self.arduino_unit.readline().decode('utf-8')
						if reading:
							yield reading
					except UnicodeDecodeError as e:
						sys.stderr.write('Decode error at ArduinoReader: %s\n' % str(e))
			except serial.serialutil.SerialException as e:
				sys.stderr.write('ArduinoReader error: %s\n' % str(e))
				logging.exception('ArduinoReader: Did not find port %s\n' % port)

	def read(self):
		return self._read_arduino


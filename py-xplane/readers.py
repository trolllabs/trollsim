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
						msg = self.arduino_unit.readline().decode('utf-8').split()
						assert len(msg) == 4
						yield list(map(float, msg))
					except AssertionError:
						error_msg = 'ArduinoReader: Unclean reading from arduino, %d\n' % len(msg)
						sys.stderr.write(error_msg)
						logging.exception(error_msg)
					except Exception as e:
						sys.stderr.write('error: %s\n' % str(e))
						logging.exception('ArduinoReader: Error when reading from serial')
			except serial.serialutil.SerialException as e:
				sys.stderr.write('ArduinoReader error: %s\n' % str(e))
				logging.exception('ArduinoReader: Did not find port %s\n' % port)

	def read(self):
		return self._read_arduino


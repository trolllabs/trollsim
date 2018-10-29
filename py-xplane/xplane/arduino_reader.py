import sys, serial, logging


class ArduinoReader:
	def __init__(self, arduino_port, baudrate):
		logging.basicConfig(level=logging.DEBUG, filename='log.txt')
		self.arduino_unit = serial.Serial(arduino_port, baudrate)

	def _read_arduino(self):
		while True:
			try:
				msg = self.arduino_unit.readline().decode('utf-8').split()
				#print('roll: %s, pitch: %s, yaw: %s' % (msg[0], msg[1], msg[2]))
				assert len(msg) == 4
				yield list(map(float, msg))
			except AssertionError:
				error_msg = 'ArduinoReader: Unclean reading from arduino, %d' % len(msg)
				sys.stderr.write(error_msg)
				logging.exception(error_msg)
			except Exception as e:
				sys.stderr.write('error: %s\n' % str(e))
				logging.exception('ArduinoReader: Error when reading from serial')

	def read(self):
		return self._read_arduino


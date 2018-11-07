import struct, sys, logging


class XPlaneConnector:
	def __init__(self):
		self.data_multipliers = {}
		self.packet_wrapper = XPlaneDataAdapter()

	def frontend_handler(self, value):
		try:
			data = value.strip().split()
			assert len(data) == 2
			self.data_multipliers[int(data[0])] = float(data[1])
		except AssertionError:
			error_msg = 'XPlaneConnector: Too many values, %d\n' % len(data)
			sys.stderr.write(error_msg)
			logging.exception(error_msg)

	def _packet_wrapper(self):
		try:
			for reading in self.data_reading():
				for i, data in enumerate(reading):
					processed_data = data*self.data_multipliers.get(i, 1)
					yield self.packet_wrapper.create_dref_packet(
							processed_data,
							'f',
							self.dref_names[i]
							)
		except Exception as e:
			sys.stderr.write('XPlaneConnector error: %s\n' % str(e))
			logging.exception('XPlaneDataAdapter._packet_wrapper: \
					Alignment between dref_names and actual reading')

	def wrap(self, data_reading, expected_reading):
		self.data_reading = data_reading
		self.dref_names = expected_reading
		return self._packet_wrapper


class XPlaneDataAdapter:
	def _null_terminate(self, s):
		return s + '\0'

	def _create_null_pad(self, pad_length):
		return ('\0'*pad_length).encode()

	def create_dref_packet(self, value, dtype, name):
		header = self._null_terminate('DREF')
		name = self._null_terminate(name)
		pad_length = 509 - (len(header) + 4 + len(name))
		pad = self._create_null_pad(pad_length)

		packer = struct.Struct('<%ds %s %ds %ds' % (len(header), dtype, len(name), pad_length))
		return packer.pack(*(header.encode(), value, name.encode(), pad))


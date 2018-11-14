import struct, sys, logging


class XPlaneConnector:
	def __init__(self, expected_reading):
		self.data_multipliers = {}
		self.packet_wrapper = XPlaneDataAdapter()
		self.dref_names = expected_reading

	def frontend_handler(self, value):
		try:
			data = value.strip().split()
			assert len(data) == 2
			self.data_multipliers[int(data[0])] = float(data[1])
		except AssertionError:
			error_msg = 'XPlaneConnector: Too many values, %d\n' % len(data)
			sys.stderr.write(error_msg)
			logging.exception(error_msg)

	def __call__(self, data_input, data_output):
		try:
			for reading in data_input():
				for i, data in enumerate(reading):
					processed_data = data*self.data_multipliers.get(i, 1)
					binary_data = self.packet_wrapper(processed_data, self.dref_names[i])
					data_output(binary_data)
		except Exception as e:
			sys.stderr.write('XPlaneConnector error: %s\n' % str(e))
			logging.exception('XPlaneDataAdapter._packet_wrapper: \
					Alignment between dref_names and actual reading')


class XPlaneDataAdapter:
	def __init__(self):
		# Use signed integer type when assigning boolean packet values
		self.XP_True = 0x3F800000
		self.XP_False = 0x00000000
		self.dtype_lookup = {float: 'f', int: 'i'}

	def _null_terminate(self, s):
		return s + '\0'

	def _create_null_pad(self, pad_length):
		return ('\0'*pad_length).encode()

	def _xplane_boolean(self, arg):
		xp_bool = self.XP_False
		if arg:
			xp_bool = self.XP_True
		return 'i', xp_bool

	def wrap(self, value, name, dtype):
		header = self._null_terminate('DREF')
		name = self._null_terminate(name)
		pad_length = 509 - (len(header) + 4 + len(name))
		pad = self._create_null_pad(pad_length)

		packer = struct.Struct('<%ds %s %ds %ds' % (len(header), dtype, len(name), pad_length))
		return packer.pack(*(header.encode(), value, name.encode(), pad))

	def __call__(self, value, name, dtype=None):
		if type(value) == bool:
			dtype, value = self._xplane_boolean(value)
		if not dtype:
			dtype = self.dtype_lookup[type(value)]
		return self.wrap(value, name, dtype)


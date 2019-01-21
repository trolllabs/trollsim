import struct


''' Misc

General tools for mostly variable lookup and data conversion, including
to and from DREF (format defined by X-Plane).
'''


expected_glove_data = {
		0: 'sim/test/test_float',
		1: 'sim/joystick/yoke_roll_ratio',
		2: 'sim/joystick/yoke_pitch_ratio',
		3: 'sim/joystick/yoke_heading_ratio'
		}


class XPlaneDataAdapter:
	'''
	Can convert data from and to dataref (dref), which is X-Plane's
	pre-defined packet structure. Use parse_to_dref and parse_from_dref
	methods.

	If dtype_lookup does not contain the value to convert to dref, wrap
	is also possible to use to manually set the datatype.
	'''
	def __init__(self):
		# Use signed integer type when assigning boolean packet values
		self.XP_True = 0x3F800000
		self.XP_False = 0x00000000
		self.dtype_lookup = {float: 'f', int: 'i'}

	def _null_terminate(self, s):
		return s + '\0'

	def _create_null_pad(self, pad_length):
		return ('\0'*pad_length).encode()

	def _xplane_boolean(self, arg: bool):
		'''
		Convert argument to a format X-Plane accepts as boolean value.
		'''
		xp_bool = self.XP_False
		if arg:
			xp_bool = self.XP_True
		return 'i', xp_bool

	def wrap(self, value, name, dtype):
		'''
		Builds a dref packet with binary values.
		'''
		header = self._null_terminate('DREF')
		name = self._null_terminate(name)
		pad_length = 509 - (len(header) + 4 + len(name))
		pad = self._create_null_pad(pad_length)

		packer = struct.Struct('<%ds %s %ds %ds' % (len(header), dtype, len(name), pad_length))
		return packer.pack(*(header.encode(), value, name.encode(), pad))

	def parse_to_dref(self, value, name, dtype=None):
		if type(value) == bool:
			dtype, value = self._xplane_boolean(value)
		if not dtype:
			dtype = self.dtype_lookup[type(value)]
		return self.wrap(value, name, dtype)

	def parse_from_dref(self, packet):
		'''
		Currently only supports float datarefs
		'''
		name = str(packet[9:].strip(b'\x00'))
		raw_value = packet[5:9]
		value = struct.unpack('f', raw_value)[0]
		return name, value


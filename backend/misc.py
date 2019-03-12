import struct
from time import perf_counter


''' Misc

General tools for mostly variable lookup and data conversion, including
to and from DREF (format defined by X-Plane).
'''


expected_glove_data = {
		0: 'sim/cockpit2/engine/actuators/throttle_ratio_all',
		1: 'sim/joystick/yoke_roll_ratio',
		2: 'sim/joystick/yoke_pitch_ratio',
		3: 'sim/joystick/yoke_heading_ratio'
		}


type_lookup = {
		'float': 'f',
		'int': 'i',
		float: 'f',
		int: 'i'
		}




import threading
class Observable:
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


class XPlaneDataAdapter:
	'''
	Can convert data from and to dataref (dref), which is X-Plane's
	pre-defined packet structure. Use parse_to_dref and parse_from_dref
	methods.

	If type_lookup does not contain the value to convert to dref, wrap
	is also possible to use to manually set the datatype.
	'''
	def __init__(self):
		# Use signed integer type when assigning boolean packet values
		self.XP_True = 0x3F800000
		self.XP_False = 0x00000000

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

	def parse_to_dref(self, name, value, dtype=None):
		if type(value) == bool:
			dtype, value = self._xplane_boolean(value)
		if not dtype:
			dtype = type_lookup[type(value)]
		return self.wrap(value, name, dtype)

	def parse_from_dref(self, packet):
		'''
		Currently only supports float datarefs
		'''
		name = packet[9:].strip(b'\x00').decode('utf-8')
		raw_value = packet[5:9]
		value = struct.unpack('f', raw_value)[0]
		return name, value


class PacketFactory:
	def __init__(self, config):
		self.lookup = config

	def to_binary(self, data_id, data):
		return struct.pack('>B %s' % type_lookup[type(data)], data_id, data)

	def from_binary(self, binary_packet):
		packet_id = binary_packet[0]
		metadata = self.lookup['ids'][str(packet_id)]
		metadata['id'] = packet_id
		return TrollPacket(metadata, binary_packet=binary_packet)

	def from_name(self, name, value):
		metadata = self.lookup['names'][name]
		metadata['name'] = name
		metadata['id'] = int(metadata['id'])
		return TrollPacket(metadata, value=value)


class TrollPacket:
	'''
	Internal data representation.

	Args:
		raw_data (binary): Packet data
		data (int/float):  Interpreted packet data
	'''
	def __init__(self, metadata, value=None, binary_packet=None):
		if (binary_packet == None) and (value == None):
			msg = 'TrollPacket: Missing value. (Was the packet instanciated outside PacketFactory?)'
			raise ValueError(msg)
		elif binary_packet == value:
			msg = 'TrollPacket: binary and value should not be the same'
			raise AttributeError(msg)
		self.metadata = metadata
		self.binary_packet = binary_packet
		self.timestamp = int(perf_counter()*1000)
		self.data = value

	@property
	def id(self):
		return self.metadata['id']

	@property
	def type(self):
		return self.metadata['type']

	@property
	def name(self):
		return self.metadata['name']

	@property
	def binary(self):
		if self.binary_packet == None:
			structure = '>B %s' % type_lookup[self.type]
			self.binary_packet = struct.pack(structure, self.id, self.value)
		return self.binary_packet

	@property
	def binary_value(self):
		return self.binary[1:]

	def from_binary(self, binary_value):
		return struct.unpack('>' + type_lookup[self.type], binary_value)[0]

	@property
	def value(self):
		if self.data == None:
			self.data = self.from_binary(self.binary_value)
		return self.data

	@property
	def hex(self):
		return '0x' + self.binary.hex().upper()

	@property
	def hex_value(self):
		return '0x' + self.binary_value.hex().upper()

	def _native_typecheck(self, value):
		if type(value) == TrollPacket:
			value = value.value
		return value

	def _new_packet(self, new_value):
		return TrollPacket(self.metadata, value=new_value)

	def __add__(self, addend):
		addend = self._native_typecheck(addend)
		return self._new_packet(self.value + addend)

	def __radd__(self, addend):
		return self.__add__(addend)

	def __sub__(self, subtrahend):
		subtrahend = self._native_typecheck(subtrahend)
		return self._new_packet(self.value - subtrahend)

	def __rsub__(self, minuend):
		minuend = self._native_typecheck(minuend)
		return self._new_packet(minuend - self.value)

	def __mul__(self, factor):
		factor = self._native_typecheck(factor)
		if self.metadata['type'] == 'int' and not factor.is_integer():
			factor = int(factor)
		return self._new_packet(self.value*factor)

	def __rmul__(self, factor):
		return self.__mul__(factor)

	def __truediv__(self, divisor):
		divisor = self._native_typecheck(divisor)
		if divisor == 0: # divide by zero
			# TODO: there are challenges here...
			return self._new_packet(-1)
		elif self.metadata['type'] == 'int':
			return self._new_packet(int(self.value//divisor))
		else:
			return self._new_packet(self.value/divisor)

	def __rtruediv__(self, dividend):
		dividend = self._native_typecheck(dividend)
		if self.value == 0:
			# same problem
			return self._new_packet(-1)
		elif self.metadata['type'] == 'int':
			return self._new_packet(int(dividend//self.value))
		else:
			return self._new_packet(dividend/self.value)

	def __str__(self):
		retval = '%s' % type(self).__name__
		classvars = vars(self)
		retval += '\n\thex: %s' % self.hex
		retval += '\n\tvalue: %s' % self.value
		for var in classvars.keys():
			retval += '\n\t%s: %s' % (var, classvars[var])
		return retval


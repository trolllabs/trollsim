import struct
from time import perf_counter
from misc import type_lookup


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
		self.module_id = -1

		if type(value) == str:
			if metadata['type'] == 'float':
				self.data = float(value)
			elif 'int' in metadata['type']:
				self.data = int(value)
			else:
				raise ValueError('Metadata error. %s' % metadata)
		else:
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
			retval = value.value
		else:
			retval = value
		return retval

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


"""
.. module:: datastructures

Currently the only datastructure in TrollSim is TrollPacket.
"""

import struct
from time import perf_counter
from misc import type_lookup


class TrollPacket:
	"""
	Internal datapoint representation.

	Args:
		raw_data (binary): Packet data
		data (int/float):  Interpreted packet data
	"""
	meta = None
	def __init__(self, packet_meta, binary_packet, value=None):
		"""
		A standardized network packet, or "TrollSim network packet" is
		used when describing a binary packet with:
		- First byte as ID
		- Last four bytes as value (float/int)

		:param packet_meta: A dictionary with keywords 'name', 'id' and
		'type'.
		:param binary_packet: A standardized network packet
		:param value: If binary_packet is derived from value, just pass
		value as argument here.

		:type packet_meta: dict
		:type binary_packet: bytes
		:type value: int/float
		"""
		self.binary_packet = binary_packet
		self.metadata = packet_meta
		self.timestamp = int(perf_counter()*1000)
		self.module_id = -1
		if value:
			self.value = value
		else:
			self.value = self.from_binary(self.binary_value)

	def _cast_value(metadata, value):
		if type(value) == str:
			if 'float' in metadata['type']:
				value = float(value)
			elif 'int' in metadata['type']:
				value = int(value)
			else:
				raise ValueError('Metadata error. %s' % metadata)
		return value

	def _create_network_packet(packet_meta, value):
		"""
		Creates a TrollSim network packet, bin(ID (1) + value (4))

		:param packet_meta: Dictionary with keywords for 'name', 'id'
		and 'type'
		:param value: Packet value

		:type packet_meta: dict
		:type value: float/int

		:return: TrollSim network packet
		"""
		return struct.pack('>B %s' % type_lookup[type(value)], packet_meta['id'], value)

	def _create_packet(packet_meta, value):
		"""
		Creates a TrollPacket from int or float value.

		:param packet_meta: Dictionary with keywords for 'name', 'id'
		and 'type'
		:param value: Packet value

		:type packet_meta: dict
		:type value: float/int

		:return: TrollPacket
		"""
		packet_value = TrollPacket._cast_value(packet_meta, value)
		binary_packet = TrollPacket._create_network_packet(packet_meta, packet_value)
		return TrollPacket(packet_meta, binary_packet, value)

	def from_name(name, value):
		"""
		Extracts relevant metadata based on the name argument before
		using self._create_packet to instantiate a TrollPacket.

		:param name: A name which can be found in metadata.txt
		:param value: Packet value

		:type name: str
		:type value: float/int

		:return: TrollPacket
		"""
		packet_meta = TrollPacket.meta['names'][name]
		return TrollPacket._create_packet(packet_meta, value)

	def from_id(packet_id, value):
		"""
		Extracts relevant metadata based on the packet_id argument
		before using self._create_packet to instantiate a TrollPacket.

		:param packet_id: An ID which can be found in metadata.txt
		:param value: Packet value

		:type packet_id: uint8
		:type value: float/int

		:return: TrollPacket
		"""
		packet_meta = TrollPacket.meta['ids'][str(packet_id)]
		return TrollPacket._create_packet(packet_meta, value)

	def from_binary_packet(network_packet):
		"""
		Extracts relevant metadata before instantiating a TrollPacket.

		:param network_packet: A TrollSim network packet
		:type network_packet: bytes

		:return: TrollPacket
		"""
		packet_meta = TrollPacket.meta['ids'][str(network_packet[0])]
		return TrollPacket(packet_meta, network_packet)

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
		binary_packet = TrollPacket._create_network_packet(self.metadata, new_value)
		return TrollPacket(self.metadata, binary_packet, new_value)

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
		"""
		String representation of the object.
		Prints various states of interest in formatted text.
		"""
		retval = '%s' % type(self).__name__
		classvars = vars(self)
		retval += '\n\thex: %s' % self.hex
		for var in classvars.keys():
			retval += '\n\t%s: %s' % (var, classvars[var])
		return retval


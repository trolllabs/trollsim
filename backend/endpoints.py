"""
.. module:: endpoints

The endpoint collection is an abstraction layer which parses incoming
data into a known format, TrollPacket and outgoing TrollPackets to a
required format, such as X-Plane's dataref or similar.
"""

import struct, json, sys, logging
from threading import Thread
from protocols import UDPClient, UDPServer, TCPServer, TCPClient, Serial, Bluetooth
from datastructures import TrollPacket
from misc import type_lookup, DtypeConverter
from patterns import Observable


class ObservableComponent(Observable, Thread):
	"""
	Parent class for endpoints in TrollSim.
	All children classes can be subscribed (Observable) and are
	threaded (Thread) by default. See ObservableComponent.run() for
	startup semantics.

	Inclues methods such as test_write for debugging, fallback methods
	for unimplemented parse_data and write (throws exception).
	Also thread management methods such as starting and stopping threads.
	"""
	def __init__(self, data_source, extra_protocols=[]):
		"""
		Has fields for module ID and its running status for later
		referencing. The data_source and extra_protocols arguments are
		for later collective closing when the module is shut down.
		"""
		Observable.__init__(self)
		Thread.__init__(self)
		self.protocols = extra_protocols
		self.data_source = data_source
		self.id = -1
		self.name = type(self).__name__
		self.running = True

	def parse_data(self):
		"""
		If the endpoints will be receiving data, this method needs to be
		implemented/overwritten in the child class.
		"""
		raise NotImplementedError('%s: No parse function implemented!' % self.name)

	def write(self):
		"""
		If the endpoints will be sending data, this method needs to be
		implemented/overwritten in the child class.
		"""
		raise NotImplementedError('%s: No write function implemented!' % self.name)

	def test_write(self, packet_id, value):
		"""
		Method used for testing network. Not used in deployment.

		:param packet_id: id of the packet
		:type packet_id: int

		:param value: value of the packet
		:type value: int/float
		"""
		packet = struct.pack('>B %s' % type_lookup[type(value)], data_id, value)
		print('%s Testpacket: 0x%s' % (self.name, packet.hex().upper()))
		self.data_source.send(packet)

	def update_listeners(self, packet):
		"""
		Set the origin id in a packet, so the packet can be tracked.
		All endpoint classes should use this for passing packets
		further.

		:param packet: A TrollPacket with instantiated values
		:type packet: TrollPacket
		"""
		packet.module_id = self.id
		self._notify_listeners(packet)

	def run(self):
		"""
		Inherited from Thread. Is called when the object is
		instantiated.
		"""
		self.data_source.connect()
		while self.running:
			self.data_source.read()

	def stop(self):
		"""
		Called when the one wants to close the module.
		"""
		self.running = False
		self.data_source.close()
		for protocol in self.protocols:
			protocol.close()
		print('%s IO closed' % self.name)


class XPlane(ObservableComponent):
	"""
	Manages all incoming and outgoing connections between.
	Converts TrollPacket to dataref format for outbound data and
	dataref to TrollPacket for inbound data.
	"""
	def __init__(self, config):
		"""
		:param config: Dictionary containing connection headers
		:type config: dict
		"""
		self.xp_write = UDPClient(config['write'])
		self.xp_read = UDPServer(config['read'])
		self.xp_read.add_listener(self.parse_data)

		self.dref_length = 509
		self.header = 'DREF'
		self.header_length = len(self.header)
		self.dref_header = struct.pack('<%ds' % self.header_length, self.header.encode())

		ObservableComponent.__init__(self, self.xp_read, [self.xp_write])

	def _null_terminate(self, s):
		return s + '\0'

	def _create_null_pad(self, pad_length):
		return b'\0'*pad_length

	def _xplane_boolean(self, is_true: bool):
		"""
		Convert argument to a format X-Plane accepts as boolean value.

		:param is_true: A bool to be converted to X-Plane accepted bool
		:type is_true: bool

		:return: Tuple with struct datatype and value representing X-Plane bool
		"""
		xp_bool = 0x00000000
		if is_true:
			xp_bool = 0x3F800000
		return 'i', xp_bool

	def wrap(self, value, name, dtype):
		"""
		Builds a dref packet with binary values.

		:param value: The value of the to-be dataref packet
		:param name: Dataref name of the to-be dataref packet
		:param dtype: Datatype of the to-be dataref packet

		:type value: int/float
		:type name: str
		:type dtype: str

		:return: Dataref packet (binary)
		"""
		header = self._null_terminate('DREF')
		name = self._null_terminate(name)
		pad_length = 509 - (len(header) + 4 + len(name))
		pad = self._create_null_pad(pad_length)

		packer = struct.Struct('<%ds %s %ds %ds' % (len(header), dtype, len(name), pad_length))
		return packer.pack(*(header.encode(), value, name.encode(), pad))

	def parse_to_dref(self, name, value, dtype=None):
		"""
		Type inference the value of a to-be dataref packet by default.

		:param name: Dataref name
		:param value: Value of the to-be dataref packet
		:param dtype: Datatype of the to-be dataref packet

		:type name: str
		:type value: int/float/bool
		:type dtype: str

		:return: Dataref packet (binary)
		"""
		if type(value) == bool:
			dtype, value = self._xplane_boolean(value)
		if not dtype:
			dtype = type_lookup[type(value)]
		return self.wrap(value, name, dtype)

	def parse_from_dref(self, packet):
		"""
		Parses a dataref packet into a string dataref name and its
		value.

		(Currently only supports float datarefs)

		:param packet: Dataref packet (binary)
		:type packet: bytes

		:return: Tuple with name (str) and value (float)
		"""
		name = packet[9:].strip(b'\x00').decode('utf-8')
		raw_value = packet[5:9]
		value = struct.unpack('f', raw_value)[0]
		return name, value

	def write(self, trollpacket):
		"""
		Converts a TrollPacket into a dataref packet before sending.

		:param trollpacket: TrollPacket with dataref name
		:type trollpacket: TrollPacket
		"""
		packet = self.parse_to_dref(trollpacket.name, trollpacket.value)
		self.xp_write.send(packet)

	def parse_data(self, data):
		"""
		Converts a dataref packet into TrollPacket before passing it
		further internally to subscribers (through Observable).

		:param data: Dataref packet (binary)
		:type data: bytes
		"""
		name, value = self.parse_from_dref(data)
		packet = TrollPacket.from_name(name, value)
		self.update_listeners(packet)


class WebUI(ObservableComponent):
	"""
	Frontend layer for handling metadata requests.
	"""
	def __init__(self, config):
		"""
		:param config: Dictionary containing connection headers
		:type config: dict
		"""
		self.frontend = TCPServer(config)
		self.frontend.add_listener(self.parse_data)

		ObservableComponent.__init__(self, self.frontend)

	def write(self, trollpacket):
		if self.frontend.ready:
			self.frontend.send(trollpacket.binary)

	def parse_data(self, data):
		if len(data) == len('meta') and 'meta' in data.decode('utf-8'):
			print('WebUI: Metadata requested')
			self.frontend.send(json.dumps(TrollPacket.meta).encode('utf-8'))
		else:
			packet = TrollPacket.from_binary_packet(data)
			self.update_listeners(packet)


class Arduino(ObservableComponent):
	"""
	Arduino layer for handling data inconsistensies.
	"""
	def __init__(self, config):
		"""
		:param config: Dictionary containing connection headers
		:type config: dict
		"""
		self.arduino = Serial(config)
		self.arduino.add_listener(self.parse_data)
		ObservableComponent.__init__(self, self.arduino)

	def parse_data(self, reading):
		"""
		Arduino sends data incosistently sometimes. This implementation
		assumes a format when receiving from arduino:

		- First byte as ID
		- Last four bytes as int32 or float32

		In total, 5 bytes. Otherwise, the reading is considered garbage
		and printed/logged as error.

		:param reading: Bytedata from arduino with newline at end removed
		:type reading: bytes
		"""
		if len(reading) == 5:
			try:
				packet = TrollPacket.from_binary_packet(reading)
				self.update_listeners(packet)
			except KeyError as e:
				err_msg = 'Arduino metadata %s. Binary packet: %s' % (e, reading.hex().upper())
				logging.exception(err_msg)


class iMotions(ObservableComponent):
	"""
	iMotions layer, for handling iMotions packet formats.
	The logged data fields are in self.sensors.

	TODO: This sensordata field implementation should be written to
	handle both with acceleration fields on/off and heartrate on/off.

	TODO: Should also have a toggle of some sort for the TCP
	communication with iMotions as both UDP and TCP is possible.
	"""
	def __init__(self, config):
		"""
		:param config: Dictionary containing connection headers
		:type config: dict
		"""
		self.receiver = UDPServer(config)
		self.receiver.add_listener(self.parse_data)
		self.sensors = {
				'Shimmer/GSR': {
					'GSR CAL (μSiemens)': 12
				},
				'Shimmer/ECG': {
					'ECG LL-RA CAL (mVolts)': 12,
					'ECG LA-RA CAL (mVolts)': 14,
					'ECG Vx-RL CAL (mVolts)': 17,
					'Heart Rate ECG LL-RA (Beats/min)' : 18
				}
			}
		ObservableComponent.__init__(self, self.receiver)

	def notify(self, packet):
		"""
		Since parse_data has multiple 'exits', this is for easier
		(print) debugging. All exits converges here except for KeyError
		"""
		self.update_listeners(packet)

	def parse_data(self, imotions_packet):
		"""
		Picks out recognized fields from an imotions packet.
		Recognized fields are listed in iMotions.sensors dictionary.

		:param imotions_packet: A packet received from imotions.
		:type imotions_packet: str
		"""
		imotions_packet = imotions_packet.decode('utf-8').strip()
		data = imotions_packet.split(';')
		if data[1] in self.sensors:
			sensor = self.sensors[data[1]]
			for channel in sensor:
				index = sensor[channel]
				packet = TrollPacket.from_name(channel, data[index])
				self.notify(packet)
		elif data[1] == 'AttentionTool':
			print(data)
			if data[2] == 'ExposureStatistics':
				print(imotions_packet) # Skip
			elif data[2] in TrollPacket.meta['names']:
				timestamp = data[5]
				packet = TrollPacket.from_name(data[2], timestamp[8:])
				print(packet)
				self.notify(packet)
		else:
			raise KeyError('Unknown iMotions packet: %s. Full packet: %s' % (data[1], data))


class TCPSocket(ObservableComponent):
	"""
	Generic TCP endpoint layer.
	"""
	def __init__(self, config):
		"""
		:param config: Dictionary containing connection headers
		:type config: dict
		"""
		self.sender = TCPClient(config)
		ObservableComponent.__init__(self, self.sender)

	def write(self, packet):
		self.sender.send(packet.binary)


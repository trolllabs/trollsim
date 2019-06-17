import struct, json, sys, logging
from threading import Thread
from protocols import UDPClient, UDPServer, TCPServer, TCPClient, Serial, Bluetooth
from datastructures import TrollPacket
from misc import type_lookup
from patterns import Observable


class ObservableComponent(Observable, Thread):
	def __init__(self, data_source, extra_protocols=[]):
		Observable.__init__(self)
		Thread.__init__(self)
		self.protocols = extra_protocols
		self.data_source = data_source
		self.id = -1
		self.name = type(self).__name__
		self.running = True

	def parse_data(self):
		raise NotImplementedError('%s: No parse function implemented!' % self.name)

	def write(self):
		raise NotImplementedError('%s: No write function implemented!' % self.name)

	def test_write(self, packet_id, value):
		packet = struct.pack('>B %s' % type_lookup[type(value)], data_id, value)
		print('%s Testpacket: 0x%s' % (self.name, packet.hex().upper()))
		self.data_source.send(packet)

	def update_listeners(self, packet):
		packet.module_id = self.id
		self._notify_listeners(packet)

	def run(self):
		self.data_source.connect()
		while self.running:
			self.data_source.read()

	def stop(self):
		self.running = False
		self.data_source.close()
		for protocol in self.protocols:
			protocol.close()
		print('%s IO closed' % self.name)


class XPlane(ObservableComponent):
	'''
	Explain why read and write socket
	'''
	def __init__(self, config):
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
		'''
		xp_bool = 0x00000000
		if is_true:
			xp_bool = 0x3F800000
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

	def write(self, trollpacket):
		packet = self.parse_to_dref(trollpacket.name, trollpacket.value)
		self.xp_write.send(packet)

	def parse_data(self, data):
		name, value = self.parse_from_dref(data)
		packet = TrollPacket.from_name(name, value)
		self.update_listeners(packet)


class WebUI(ObservableComponent):
	def __init__(self, config):
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
	def __init__(self, config):
		self.arduino = Serial(config)
		self.arduino.add_listener(self.parse_data)
		ObservableComponent.__init__(self, self.arduino)

	def parse_data(self, reading):
		if len(reading) == 5:
			try:
				packet = TrollPacket.from_binary_packet(reading)
				self.update_listeners(packet)
			except KeyError as e:
				err_msg = 'Arduino metadata %s. Binary packet: %s' % (e, reading.hex().upper())
				logging.exception(err_msg)


class iMotions(ObservableComponent):
	def __init__(self, config):
		self.receiver = UDPServer(config)
		self.receiver.add_listener(self.parse_data)
		self.sensors = {
				'Shimmer/GSR': {
					'GSR CAL (μSiemens)': 12
				},
				'Shimmer/ECG': {
					'ECG LL-RA CAL (mVolts)': 12,
					'ECG LA-RA CAL (mVolts)': 14,
					'ECG Vx-RL CAL (mVolts)': 17
				}
			}
		ObservableComponent.__init__(self, self.receiver)

	def notify(self, packet):
		'''
		Since parse_data has multiple 'exits', this is for easier
		(print) debugging. All exits converges here except for KeyError
		'''
		self.update_listeners(packet)

	def parse_data(self, imotions_packet):
		imotions_packet = imotions_packet.decode('utf-8').strip()
		data = imotions_packet.split(';')
		if data[1] in self.sensors:
			sensor = self.sensors[data[1]]
			for channel in sensor:
				index = sensor[channel]
				packet = TrollPacket.from_name(channel, data[index])
				self.notify(packet)
		elif data[1] == 'AttentionTool':
			if data[2] == 'ExposureStatistics':
				print(imotions_packet) # Skip
			elif data[2] in TrollPacket.meta['names']:
				timestamp = data[5]
				packet = TrollPacket.from_name(data[2], timestamp[8:])
				self.notify(packet)
		else:
			raise KeyError('Unknown iMotions packet: %s. Full packet: %s' % (data[1], data))


class TCPSocket(ObservableComponent):
	def __init__(self, config):
		self.sender = TCPClient(config)
		ObservableComponent.__init__(self, self.sender)

	def write(self, packet):
		self.sender.send(packet.binary)


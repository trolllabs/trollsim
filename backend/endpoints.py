import struct, json, sys, logging
from threading import Thread
from protocols import UDPClient, UDPServer, TCPServer, TCPClient, Serial, Bluetooth
from datastructures import TrollPacket
from misc import type_lookup, XPlaneDataAdapter
from patterns import Observable


class ObservableComponent(Observable, Thread):
	def __init__(self, data_source, extra_protocols=[]):
		Observable.__init__(self)
		Thread.__init__(self)
		self.protocols = extra_protocols
		self.data_source = data_source
		self.endpoint_id = -1
		self.endpoint_name = type(self).__name__
		self.running = True

	@property
	def name(self):
		return self.endpoint_name

	@name.setter
	def name(self, endpoint_name):
		self.endpoint_name = endpoint_name

	@property
	def id(self):
		return self.endpoint_id

	@id.setter
	def id(self, endpoint_id):
		self.endpoint_id = endpoint_id

	def parse_data(self):
		raise NotImplementedError('%s: No parse function implemented!' % self.name)

	def write(self):
		raise NotImplementedError('%s: No write function implemented!' % self.name)

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

		ObservableComponent.__init__(self, self.xp_read, [self.xp_write])
		self.adapter = XPlaneDataAdapter()

	def write(self, trollpacket):
		packet = self.adapter.parse_to_dref(trollpacket.name, trollpacket.value)
		self.xp_write.send(packet)

	def external_write(self, name, value):
		'''
		Creates a TrollPacket from scratch instead of reading straight from one.
		The data should be created through another endpoint, which is why trollpacket
		should be the only accepted write argument.
		Intended for debugging purposes.
		'''
		packet = TrollPacket.from_name(name, value)
		self.write(packet)

	def parse_data(self, data):
		name, value = self.adapter.parse_from_dref(data)
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

	def external_write(self, data_id, value):
		packet = struct.pack('>B i', data_id, value)
		print('0x' + packet.hex().upper())
		self.frontend.send(packet)

	def parse_data(self, data):
		if 'metadata' in data.decode('utf-8'):
			print('WebUI: Metadata requested')
			self.frontend.send(json.dumps(TrollPacket.meta).encode('utf-8'))
		else:
			packet = TrollPacket(data)
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
				print(packet)
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


class AudioSocket(ObservableComponent):
	def __init__(self, config):
		self.sender = TCPClient(config)
		ObservableComponent.__init__(self, self.sender)

	def write(self, packet):
		self.sender.send(str(packet.value).encode('utf-8'))


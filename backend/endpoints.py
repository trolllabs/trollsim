import struct, json, sys, logging
from threading import Thread
from protocols import UDPClient, UDPServer, TCPServer, TCPClient, Serial, Bluetooth
from misc import type_lookup, XPlaneDataAdapter
from patterns import Observable, PacketFactory


class ObservableComponent(Observable, Thread):
	def __init__(self, metadata, data_source, extra_protocols=[]):
		Observable.__init__(self)
		Thread.__init__(self)
		self.protocols = extra_protocols
		self.metadata = metadata
		self.data_source = data_source
		self.packet_factory = PacketFactory(metadata)
		self.data_source.connect()
		self.endpoint_id = -1
		self.running = True

	@property
	def name(self):
		return type(self).__name__

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
	def __init__(self, config, meta):
		self.xp_write = UDPClient(config['write'])
		self.xp_read = UDPServer(config['read'])
		self.xp_read.add_listener(self.parse_data)

		ObservableComponent.__init__(self, meta, self.xp_read, [self.xp_write])
		self.packet_parser = XPlaneDataAdapter().parse_from_dref
		self.packet_wrapper = XPlaneDataAdapter().parse_to_dref

	def write(self, trollpacket):
		packet = self.packet_wrapper(trollpacket.name, trollpacket.value)
		self.xp_write.send(packet)

	def external_write(self, name, value):
		'''
		Creates a TrollPacket from scratch instead of reading straight from one.
		The data should be created through another endpoint, which is why trollpacket
		should be the only accepted write argument.
		Intended for debugging purposes.
		'''
		packet = self.packet_factory.from_name(name, value)
		self.write(packet)

	def parse_data(self, data):
		name, value = self.packet_parser(data)
		packet = self.packet_factory.from_name(name, value)
		self.update_listeners(packet)


class WebUI(ObservableComponent):
	def __init__(self, config, meta):
		self.meta = meta
		self.frontend = TCPServer(config)
		self.frontend.add_listener(self.parse_data)

		ObservableComponent.__init__(self, meta, self.frontend)

	def write(self, trollpacket):
		self.frontend.send(trollpacket.binary)

	def external_write(self, data_id, value):
		packet = struct.pack('>B i', data_id, value)
		print('0x' + packet.hex().upper())
		self.frontend.send(packet)

	def parse_data(self, data):
		if data.decode('utf-8') == 'metadata':
			self.frontend.send(json.dumps(self.meta).encode('utf-8'))
		else:
			packet = self.packet_factory.from_binary(data)
			self.update_listeners(packet)


class Arduino(ObservableComponent):
	def __init__(self, config, meta):
		self.arduino = Serial(config)
		self.arduino.add_listener(self.parse_data)
		ObservableComponent.__init__(self, meta, self.arduino)

	def parse_data(self, reading):
		if len(reading) == 5:
			try:
				packet = self.packet_factory.from_binary(reading)
				print(packet)
				self.update_listeners(packet)
			except KeyError as e:
				err_msg = 'Arduino metadata %s. Binary packet: %s' % (e, reading.hex().upper())
				logging.exception(err_msg)


class iMotions(ObservableComponent):
	def __init__(self, config, meta, log=False):
		self.receiver = UDPServer(config)
		self.receiver.add_listener(self.parse_data)
		self.fields = {
				'GSR': config['sensors']['Shimmer/GSR'],
				'ECG': config['sensors']['Shimmer/ECG'],
				}

		ObservableComponent.__init__(self, meta, self.receiver)

		self.log_file = None
		if log:
			self.log_file = open('imotions%s.log' % int(time()), 'w')

	def parse_data(self, imotions_packet):
		if self.log_file:
			self.log_file.write(imotions_packet)

		imotions_packet = imotions_packet.decode('utf-8').strip()
		data = imotions_packet.split(';')
		if data[2] in self.fields:
			id_lookup = self.fields[data[2]]
			for index in id_lookup:
				packet = self.packet_factory.from_id(id_lookup[index], data[int(index)])
				self.update_listeners(packet)
		elif data[1] == 'AttentionTool':
			pass


class AudioSocket(ObservableComponent):
	def __init__(self, config, meta):
		self.sender = TCPClient(config)
		ObservableComponent.__init__(self, meta, self.sender)

	def write(self, packet):
		self.sender.send(str(packet.value).encode('utf-8'))


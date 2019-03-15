import struct, json
from threading import Thread
from protocols import UDPClient, UDPServer, TCPServer, Serial, Bluetooth
from misc import Observable, type_lookup, XPlaneDataAdapter, PacketFactory


class ObservableComponent(Observable, Thread):
	def __init__(self, metadata, data_source):
		Observable.__init__(self)
		Thread.__init__(self)
		self.data_source = data_source
		self.packet_factory = PacketFactory(metadata)
		self.data_source.connect()

	def parse_data(self):
		raise NotImplementedError('ObservableComponent: No parse function implemented!')

	def run(self):
		while True:
			self.data_source._read()


class XPlane(ObservableComponent):
	'''
	Explain why read and write socket
	'''
	def __init__(self, config):
		self.config = config['component']['xplane']
		self.xp_write = UDPClient(self.config['write'])
		self.xp_read = UDPServer(self.config['read'])
		self.xp_read.add_listener(self.parse_data)

		ObservableComponent.__init__(self, config['metadata'], self.xp_read)
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
		self._notify_listeners(packet)


class WebUI(ObservableComponent):
	def __init__(self, config):
		self.frontend = TCPServer(config['component']['frontend'])
		self.frontend.add_listener(self.parse_data)
		self.frontend.send(json.dumps(config['metadata']).encode('utf-8'))
		ObservableComponent.__init__(self, config['metadata'], self.frontend)

	def write(self, trollpacket):
		self.frontend.send(trollpacket.binary)

	def external_write(self, data_id, value):
		packet = struct.pack('>B i', data_id, value)
		print('0x' + packet.hex().upper())
		self.frontend.send(packet)
		
	def parse_data(self, data):
		if len(data) == 5:
			packet = self.packet_factory.from_binary(data)
			self._notify_listeners(packet)


class Glove(ObservableComponent):
	def __init__(self, config):
		self.arduino = Serial(config['component']['glove'])
		self.arduino.add_listener(self.parse_data)
		ObservableComponent.__init__(self, config['metadata'], self.arduino)

	def parse_data(self, reading):
		if len(reading) == 5:
			packet = self.packet_factory.from_binary(reading)
			self._notify_listeners(packet)


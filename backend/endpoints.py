import struct, json, sys
from threading import Thread
from protocols import UDPClient, UDPServer, TCPServer, Serial, Bluetooth
from misc import type_lookup, XPlaneDataAdapter
from patterns import Observable, PacketFactory


class ObservableComponent(Observable, Thread):
	def __init__(self, metadata, data_source):
		Observable.__init__(self)
		Thread.__init__(self)
		self.metadata = metadata
		self.data_source = data_source
		self.packet_factory = PacketFactory(metadata)
		self.data_source.connect()
		self.running = True

	def parse_data(self):
		raise NotImplementedError('ObservableComponent: No parse function implemented!')

	def stop(self):
		raise NotImplementedError('ObservableComponent: No stop function implemented!')

	def run(self):
		while self.running:
			self.data_source.read()


class XPlane(ObservableComponent):
	'''
	Explain why read and write socket
	'''
	def __init__(self, config, meta):
		self.xp_write = UDPClient(config['write'])
		self.xp_read = UDPServer(config['read'])
		self.xp_read.add_listener(self.parse_data)

		ObservableComponent.__init__(self, meta, self.xp_read)
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

	def stop(self):
		self.xp_write.close()
		self.xp_read.close()
		self.running = False
		print('XPlane IO closed')


class WebUI(ObservableComponent):
	def __init__(self, config, meta):
		self.frontend = TCPServer(config)
		self.frontend.add_listener(self.parse_data)

		ObservableComponent.__init__(self, meta, self.frontend)
		self.frontend.send(json.dumps(meta).encode('utf-8'))

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

	def stop(self):
		self.frontend.close()
		self.running = False
		print('WebUI IO closed')


class Arduino(ObservableComponent):
	def __init__(self, config, meta):
		self.arduino = Serial(config)
		self.arduino.add_listener(self.parse_data)
		ObservableComponent.__init__(self, meta, self.arduino)

	def parse_data(self, reading):
		if len(reading) == 5:
			try:
				packet = self.packet_factory.from_binary(reading)
				self._notify_listeners(packet)
			except KeyError as e:
				err_msg = 'Arduino KeyError %s. Binary packet: %s' % (e, reading.hex().upper())
				sys.stderr.write(err_msg)

	def stop(self):
		self.arduino.close()
		self.running = False
		print('Arduino IO closed')


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
				self._notify_listeners(packet)
		elif data[1] == 'AttentionTool':
			pass

	def stop(self):
		self.receiver.close()
		self.running = False
		print('iMotions IO closed')


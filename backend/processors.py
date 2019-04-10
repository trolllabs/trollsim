''' Data processors

A collection of hubs where data pass through, gets possibly mutated
and sent further.
'''


class Tunnel:
	def __init__(self, input_source, output_source):
		input_source.add_listener(output_source.write)


class AudioTrigger:
	def __init__(self):
		self.endpoints = ['alarmbox', 'audiosocket']

	def send_signal(self, packet):
		if packet.id == 14:
			self.audiosocket.write(packet)
		if packet.id == 15:
			self.audiosocket.write(packet)

	def set_sources(self, endpoints: dict):
		self.alarmbox = endpoints['alarmbox']
		self.audiosocket = endpoints['audiosocket']
		self.alarmbox.add_listener(self.send_signal)


class GloveMultiplier:
	'''
	Takes a datastream from the glove arduino and multiplies it with
	self.data_multipliers. data_multipliers can be changed through
	frontend_handler, which in turn is set from the frontend.

	                    frontend (agent)
	                           |
	                           v
	[glove_arduino] -> [GloveMultiplier] -> [data output]

	[glove_arduino] -> [frontend]
	'''
	def __init__(self):
		self.multipliers = {}
		self.endpoints = ['frontend', 'glove', 'xplane']

	def update_multipliers(self, packet):
		self.multipliers[packet.name] = packet.value

	def glove_handler(self, packet):
		self.xplane.write(packet*self.multipliers.get(packet.name, 1))
		self.frontend.write(packet*self.multipliers.get(packet.name, 1))

	def set_sources(self, endpoints: dict):
		self.frontend = endpoints['frontend']
		self.xplane = endpoints['xplane']
		self.glove = endpoints['glove']
		self.glove.add_listener(self.glove_handler)
		self.frontend.add_listener(self.update_multipliers)


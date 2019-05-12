''' Data processors

A collection of hubs where data pass through, gets possibly mutated
and sent further.
'''


class Tunnel:
	def __init__(self, input_source, output_source):
		input_source.add_listener(output_source.write)


class Processor:
	def __init__(self):
		self.data_sources = {}

	def route_data(self, source, callback):
		source.add_listener(callback)
		self.data_sources[source] = callback

	def end_session(self):
		for source in self.data_sources:
			source.remove_listener(self.data_sources[source])
		self.data_sources = {}


class AudioTrigger(Processor):
	def __init__(self):
		Processor.__init__(self)
		self.endpoints = ['audiosocket', 'alarmbox-slave']

	def send_signal(self, packet):
		if packet.id == 14:
			self.audiosocket.write(packet)
		if packet.id == 15:
			self.audiosocket.write(packet)

	def set_sources(self, endpoints: dict):
		self.audiosocket = endpoints['audiosocket']
		alarmbox = endpoints['alarmbox-slave']
		self.route_data(alarmbox, self.send_signal)


class GloveMultiplier(Processor):
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
		Processor.__init__(self)
		self.multipliers = {}
		self.endpoints = ['frontend', 'glove', 'xplane']

	def update_multipliers(self, packet):
		self.multipliers[packet.name] = packet.value

	def glove_handler(self, packet):
		self.xplane.write(packet*self.multipliers.get(packet.name, 1))
		self.frontend.write(packet*self.multipliers.get(packet.name, 1))

	def set_sources(self, endpoints: dict):
		self.xplane = endpoints['xplane']
		self.frontend = endpoints['frontend']
		self.route_data(self.frontend, self.update_multipliers)

		glove = endpoints['glove']
		self.route_data(glove, self.glove_handler)


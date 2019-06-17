"""
.. module:: processors

A collection of hubs where data pass through, gets possibly mutated
and sent further.

All processor constructors must have a list with the names of modules
they need until a better logic is implemented. See implementation of
control.ControlAPI.start_processor.
"""

class Tunnel:
	"""
	A simple tunnel which output subscribes to input source where data
	is not processed.
	"""
	def __init__(self, input_source, output_source):
		input_source.add_listener(output_source.write)


class Processor:
	"""
	Parent class for all processors.

	Has a *subscribe* method for data routing, route_data and close
	method for properly closing all parties involved in data routing.
	(So use it!)
	"""
	def __init__(self):
		self.data_sources = {}

	def route_data(self, source, callback):
		"""
		Adds a source (endpoint) to data_sources for later availability
		when closing a processor in end_session.

		:param source: A data source/endpoint.
		:param callback: A subscriber to the source argument.

		:type source: ObservableComponent
		:type callback: function
		"""
		source.add_listener(callback)
		self.data_sources[source] = callback

	def end_session(self):
		"""
		Ends a processor session by removing subscribers from
		subscription list.
		"""
		for source in self.data_sources:
			source.remove_listener(self.data_sources[source])
		self.data_sources = {}


class AudioTrigger(Processor):
	"""
	Routes data with IDs 17, 18 and 19 from alarmbox-slave to
	audiosocket module.
	"""
	def __init__(self):
		Processor.__init__(self)
		self.endpoints = ['audiosocket', 'alarmbox-slave']

	def send_signal(self, packet):
		if packet.id in [17, 18, 19]:
			self.audiosocket.write(packet)

	def set_sources(self, endpoints: dict):
		self.audiosocket = endpoints['audiosocket']
		alarmbox = endpoints['alarmbox-slave']
		self.route_data(alarmbox, self.send_signal)


class ControlTrigger(Processor):
	"""
	Routes data with ID 20 from audio-control to control-socket module.
	"""
	def __init__(self):
		Processor.__init__(self)
		self.endpoints = ['control-socket', 'audio-control']

	def send_signal(self, packet):
		if packet.id in [20]:
			self.controlsocket.write(packet)

	def set_sources(self, endpoints: dict):
		self.controlsocket = endpoints['control-socket']
		audiocontrol = endpoints['audio-control']
		self.route_data(audiocontrol, self.send_signal)


class GloveMultiplier(Processor):
	'''
	Takes a datastream from the glove arduino and multiplies it with
	a number from self.multipliers and then sends to frontend/xplane

	glove -> *self.multipliers -> xplane
	glove -> *self.multipliers -> frontend

	Frontend implementation has sliders which updates data through
	GloveMultiplier.update_multipliers.

	frontend -> set self.multipliers
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


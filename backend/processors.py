import sys, logging, struct


''' Data processors

A collection of hubs where data pass through, gets possibly mutated
and sent further.
'''


class Tunnel:
	def __init__(self, input_source, output_source):
		input_source.add_listener(output_source.write)


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
	def __init__(self, glove, web, xplane):
		self.multipliers = {}
		self.web = web
		self.xplane = xplane
		glove.add_listener(self.glove_handler)
		web.add_listener(self.update_multipliers)

	def update_multipliers(self, packet):
		self.multipliers[packet.name] = packet.value

	def glove_handler(self, packet):
		self.xplane.write(packet*self.multipliers.get(packet.name, 1))
		self.web.write(packet*self.multipliers.get(packet.name, 1))



class DataWriter:
	'''
	Write all data to binary file. Each entry should be in
	big-endian. Name of file is the unix timestamp on system when
	program start up.
	'''
	def __init__(self, *args, path='.'):
		from time import perf_counter, time
		self.start_time = int(perf_counter()*1000)
		unix_timestamp = int(time())
		self.log_file = open('%s/trollsim%s.log' % (path.rstrip('/'), unix_timestamp), 'wb')
		self.endpoints = list(args)
		for endpoint in self.endpoints:
			endpoint.add_listener(self.write)

	def add_endpoint(self, endpoint):
		self.endpoints.append(endpoint)
		endpoint.add_listener(self.write)

	def write(self, packet):
		relative_timestamp = struct.pack('>i', packet.timestamp - self.start_time)
		self.log_file.write(packet.binary + relative_timestamp)
		self.log_file.flush()

	def dispose(self):
		for endpoint in self.endpoints:
			endpoint.remove_listener(self.write)
		self.log_file.close()


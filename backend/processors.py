import sys, logging, struct


''' Data processors

A collection of hubs where data pass through, gets possibly mutated
and sent further.
'''


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
		self.web.write(packet)


class DREFTunnel:
	def __init__(self, xplane, web):
		self.web = web
		xplane.add_listener(self.sendto_web)

	def sendto_web(self, packet):
		self.web.write(packet)


class PlatformWriter:
	'''
	Deprecated, possibly nonfunctional
	Reads from xplane before passing it onto the platform arduino

	[xplane] -> [PlatformWriter] -> [platform_arduino]
	'''
	def __init__(self, xplane_readsocket, platform_arduino):
		from misc import XPlaneDataAdapter
		self.packet_parser = XPlaneDataAdapter().parse_from_dref
		self.data_output = platform_arduino
		xplane_readsocket.add_listener(self.xplane_receiver)

	def xplane_receiver(self, data):
		name, value = self.packet_parser(data)
		value = int(value)
		if 'true_phi' in name:
			if abs(value) >= 90:
				self.data_output.send(0)
			else:
				self.data_output.send(value + 90)
		elif 'true_theta' in name:
			if abs(value) >= 90:
				self.data_output.send(360)
			else:
				self.data_output.send(value + 90 + 180)


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
		for arg in args:
			arg.add_listener(self.write)

	def write(self, packet):
		relative_timestamp = struct.pack('>i', packet.timestamp - self.start_time)
		self.log_file.write(packet.binary + relative_timestamp)
		self.log_file.flush()

	def dispose(self):
		self.log_file.close()


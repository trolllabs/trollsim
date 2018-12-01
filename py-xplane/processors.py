import sys, logging


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
	def __init__(self, glove_arduino, frontend, data_output):
		from xplane_tools import expected_glove_data, XPlaneDataAdapter
		self.data_multipliers = {}
		self.packet_wrapper = XPlaneDataAdapter().parse_to_dref
		self.dref_names = expected_glove_data
		self.data_output = data_output
		glove_arduino.add_listener(self.data_sender)
		glove_arduino.add_listener(frontend.send)
		frontend.add_listener(self.frontend_handler)

	def frontend_handler(self, value):
		try:
			data = value.strip().split()
			assert len(data) == 2
			self.data_multipliers[int(data[0])] = float(data[1])
		except AssertionError:
			error_msg = 'GloveMultiplier: Too many values, %d\n' % len(data)
			sys.stderr.write(error_msg)
			logging.exception(error_msg)

	def data_sender(self, reading):
		try:
			glove_data = reading.split()
			assert len(glove_data) == 4
			glove_data = list(map(float, glove_data))
			for i, data in enumerate(glove_data):
				processed_data = data*self.data_multipliers.get(i, 1)
				packet = self.packet_wrapper(processed_data, self.dref_names[i])
				self.data_output.send(packet)
		except AssertionError:
			error_msg = 'Dimension mismatch:%s|%s\n' % (reading, self.data_multipliers)
			sys.stderr.write(error_msg)
		except ValueError as e:
			error_msg = 'GloveMultiplier: Unclean reading, %s\n' % glove_data
			sys.stderr.write(error_msg)


class PlatformWriter:
	'''
	Reads from xplane before passing it onto the platform arduino

	[xplane] -> [PlatformWriter] -> [platform_arduino]
	'''
	def __init__(self, xplane_readsocket, platform_arduino):
		from xplane_tools import XPlaneDataAdapter
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


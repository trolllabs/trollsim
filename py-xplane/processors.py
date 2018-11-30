import sys, logging


class GloveMultiplier:
	def __init__(self, glove_reader, frontend_reader, data_output):
		from xplane_tools import expected_glove_data, XPlaneDataAdapter
		self.data_multipliers = {}
		self.packet_wrapper = XPlaneDataAdapter().parse_to_dref
		self.dref_names = expected_glove_data
		self.data_output = data_output
		glove_reader.add_listener(self.data_sender)
		frontend_reader.add_listener(self.frontend_handler)

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
			error_msg = 'GloveMultiplier: Unclean reading, %s\n' % reading
			sys.stderr.write(error_msg)
		except ValueError as e:
			error_msg = 'GloveMultiplier: Unclean reading, %s\n' % glove_data
			sys.stderr.write(error_msg)


class PlatformWriter:
	def __init__(self, socket_reader, platform_arduino):
		from xplane_tools import XPlaneDataAdapter
		self.packet_parser = XPlaneDataAdapter().parse_from_dref
		self.data_output = platform_arduino
		socket_reader.add_listener(self.xplane_receiver)
		platform_arduino.add_listener(print) # debug only

	def xplane_receiver(self, data):
		name, value = self.packet_parser(data)
		value = int(value)
		if 'true_phi' in name:
			print('phi: %s, %s' % (value, name))
			if abs(value) >= 90:
				self.data_output.send(0)
			else:
				self.data_output.send(value + 90)
		elif 'true_theta' in name:
			print('theta: %s, %s' % (value, name))
			if abs(value) >= 90:
				self.data_output.send(360)
			else:
				self.data_output.send(value + 90 + 180)


class FrontendSocket:
	def __init__(self, listeners, readers, frontend_socket):
		frontend_socket.add_listener(self.frontend_receiver)
		self.data_output = frontend_socket
		self.listeners = listeners
		for reader in readers:
			reader.add_listener(self.data_forwarder)

	def frontend_receiver(self, data):
		for listener in self.listeners:
			listener(data)

	def data_forwarder(self, data):
		self.data_output.send(data)

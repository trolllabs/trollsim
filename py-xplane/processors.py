import sys, logging
from _thread import start_new_thread


class GloveMultiplier:
	def __init__(self, glove_reader, frontend_reader, data_output):
		from xplane_tools import expected_reading, XPlaneDataAdapter
		self.data_multipliers = {}
		self.packet_wrapper = XPlaneDataAdapter()
		self.dref_names = expected_reading
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
				self.data_output(packet)
		except AssertionError:
			error_msg = 'GloveMultiplier: Unclean reading, %s\n' % reading
			sys.stderr.write(error_msg)
		except ValueError as e:
			error_msg = 'GloveMultiplier: Unclean reading, %s\n' % glove_data
			sys.stderr.write(error_msg)


class FrontendSocket:
	def __init__(self, handler, socket_reader, ehealth_reader, data_output):
		self.data_output = data_output
		self.data_handler = handler
		socket_reader.add_listener(self.frontend_receiver)
		ehealth_reader.add_listener(self.frontend_sender)

	def frontend_receiver(self, data):
		self.data_handler(data)

	def frontend_sender(self, data):
		self.data_output(data)


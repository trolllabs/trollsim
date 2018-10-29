import struct, socket, sys, logging


def udp_server(udp_sock, address):
	try:
		print('Binding..')
		udp_sock.bind(address)
		print('UDP: Listening to %s %s' % address)
		while True:
			data, addr = udp_sock.recvfrom(1024)
			print(data.hex().upper())
	except socket.error as e:
		sys.stderr.write('Socket Error: %s' % str(e))
	except Exception as e:
		sys.stderr.write('Error: %s' % str(e))
	finally:
		sock.close()
		print('Socket closed')
		sys.exit(0)


def udp_client(udp_sock, address, message_generator):
	messages = message_generator()
	for message in messages:
		print(message.hex())
		udp_sock.sendto(message, address)


class XPlaneConnector:
	def __init__(self):
		self.data_multipliers = {0: 0, 1: 0, 2: 0, 3: 0}
		self.packet_wrapper = XPlaneDataAdapter()

	def frontend_handler(self, value):
		try:
			data = value.strip().split()
			assert len(data) == 2
			self.data_multipliers[int(data[0])] = float(data[1])
			print(self.data_multipliers)
		except AssertionError:
			error_msg = 'XPlaneConnector: Too many values, %d' % len(data)
			sys.stderr.write(error_msg)
			logging.exception(error_msg)

	def _packet_wrapper(self):
		try:
			for reading in self.data_reading():
				for i, data in enumerate(reading):
					processed_data = data*self.data_multipliers[i]
					yield self.packet_wrapper.create_dref_packet(
							processed_data,
							'f',
							self.dref_names[i]
							)
		except Exception as e:
			sys.stderr.write('XPlaneConnector error: %s\n' % str(e))
			logging.exception('XPlaneDataAdapter._packet_wrapper: \
					Alignment between dref_names and actual reading')

	def wrap(self, data_reading, expected_reading):
		self.data_reading = data_reading
		self.dref_names = expected_reading
		return self._packet_wrapper


class XPlaneDataAdapter:
	def _null_terminate(self, s):
		return s + '\0'

	def _create_null_pad(self, pad_length):
		return ('\0'*pad_length).encode()

	def create_dref_packet(self, value, dtype, name):
		header = self._null_terminate('DREF')
		name = self._null_terminate(name)
		pad_length = 509 - (len(header) + 4 + len(name))
		pad = self._create_null_pad(pad_length)

		packer = struct.Struct('<%ds %s %ds %ds' % (len(header), dtype, len(name), pad_length))
		return packer.pack(*(header.encode(), value, name.encode(), pad))



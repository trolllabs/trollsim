import struct
from time import perf_counter


''' Misc

General tools for mostly variable lookup and data conversion, including
to and from DREF (format defined by X-Plane).
'''


type_lookup = {
		'float': 'f',
		'int': 'i',
		float: 'f',
		int: 'i'
		}


def metadata_parser(f):
	'''
	txt -> dict
	'''
	metadata = {'ids': {}, 'names': {}}
	for line in f:
		line = line.strip().split(';')
		if (line[0] in metadata['ids'] or line[1] in metadata['names']):
			print('Warning: overlapping entry on id %s or name "%s"' % (line[0], line[1]))

		entry = {
				'id': int(line[0]),
				'name': line[1],
				'type': line[2]
				}

		metadata['ids'][line[0]] = entry
		metadata['names'][line[1]] = entry
	return metadata


class XPlaneDataAdapter:
	'''
	Can convert data from and to dataref (dref), which is X-Plane's
	pre-defined packet structure. Use parse_to_dref and parse_from_dref
	methods.

	If type_lookup does not contain the value to convert to dref, wrap
	is also possible to use to manually set the datatype.
	'''
	def __init__(self):
		# Use signed integer type when assigning boolean packet values
		self.XP_True = 0x3F800000
		self.XP_False = 0x00000000

	def _null_terminate(self, s):
		return s + '\0'

	def _create_null_pad(self, pad_length):
		return ('\0'*pad_length).encode()

	def _xplane_boolean(self, arg: bool):
		'''
		Convert argument to a format X-Plane accepts as boolean value.
		'''
		xp_bool = self.XP_False
		if arg:
			xp_bool = self.XP_True
		return 'i', xp_bool

	def wrap(self, value, name, dtype):
		'''
		Builds a dref packet with binary values.
		'''
		header = self._null_terminate('DREF')
		name = self._null_terminate(name)
		pad_length = 509 - (len(header) + 4 + len(name))
		pad = self._create_null_pad(pad_length)

		packer = struct.Struct('<%ds %s %ds %ds' % (len(header), dtype, len(name), pad_length))
		return packer.pack(*(header.encode(), value, name.encode(), pad))

	def parse_to_dref(self, name, value, dtype=None):
		if type(value) == bool:
			dtype, value = self._xplane_boolean(value)
		if not dtype:
			dtype = type_lookup[type(value)]
		return self.wrap(value, name, dtype)

	def parse_from_dref(self, packet):
		'''
		Currently only supports float datarefs
		'''
		name = packet[9:].strip(b'\x00').decode('utf-8')
		raw_value = packet[5:9]
		value = struct.unpack('f', raw_value)[0]
		return name, value


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

	def dispose(self):
		for endpoint in self.endpoints:
			endpoint.remove_listener(self.write)
		self.log_file.close()


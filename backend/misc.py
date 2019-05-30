import struct, json, argparse, sys, logging, os


''' Misc

General tools for mostly variable lookup and data conversion, including
to and from DREF (format defined by X-Plane).
'''


class ArgparseHelper(argparse.ArgumentParser):
	def error(self, message):
		sys.stderr.write('error: %s\n' % message)
		self.print_help()
		sys.exit(2)


def unhandled_exception_callback(e_type, e_value, e_traceback):
	if issubclass(e_type, KeyboardInterrupt):
		sys.__excepthook__(e_type, e_value, e_traceback)
	else:
		logging.exception('Uncaught exception', exc_info=(e_type, e_value, e_traceback))


def load_configs(args):
	with open(args.file, 'r') as f:
		component_config = json.load(f)
	with open(args.meta, 'r') as f:
		metadata_config = metadata_parser(f)
	return component_config, metadata_config


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


class DtypeConverter:
	int32_struct = struct.Struct('>i')
	float_struct = struct.Struct('>f')
	char_struct = struct.Struct('>B')

	int32_pack = int32_struct.pack
	float_pack = float_struct.pack
	char_pack = char_struct.pack

	int32_unpack = int32_struct.unpack
	float_unpack = float_struct.unpack

	float_packet_pack = struct.Struct('>B f').pack
	int_packet_pack = struct.Struct('>B i').pack

	def int_to_bin(val):
		return DtypeConverter.int32_pack(val)

	def float_to_bin(val):
		return DtypeConverter.float_pack(val)

	def char_to_bin(val):
		return DtypeConverter.char_pack(val)

	def bin_to_int(bin_val):
		return DtypeConverter.int32_unpack(bin_val)

	def bin_to_float(bin_val):
		return DtypeConverter.float_unpack(bin_val)

	def float_to_packet(packet_id, float_val):
		return float_packet_pack(packet_id, float_val)

	def int_to_packet(packet_id, float_val):
		return int_packet_pack(packet_id, float_val)


class DataWriter:
	'''
	Write all data to binary file. Each entry should be in
	big-endian. Name of file is the unix timestamp on system when
	program start up.
	'''
	def __init__(self, config, meta, path='.'):
		from time import perf_counter, time
		from os import mkdir
		self.start_time = int(perf_counter()*1000)
		unix_timestamp = int(time())
		self.logging_modules = {}
		self.endpoints = []
		self.config = config
		self.meta = meta

		try:
			logpath = '%s/log%s' % (path.rstrip('/'), unix_timestamp)
			os.mkdir(logpath)
			self.log_file = open(logpath + '/log.bin', 'wb')
			self.log_modules = open(logpath + '/modules.json', 'w')
			self.config_file = open(logpath + '/config.json', 'w')
			self.meta_file = open(logpath + '/metadata.json', 'w')
		except FileExistsError as e:
			logging.exception('Cannot overwrite directory %s.' % logpath)
			raise IOError(logpath) from e

	def assign_module_id(self, endpoint, module_id):
		if endpoint.name in self.logging_modules:
			endpoint.id = self.logging_modules[endpoint.name]
		else:
			endpoint.id = module_id
			self.logging_modules[endpoint.name] = endpoint.id

	def add_endpoint(self, endpoint):
		self.assign_module_id(endpoint, len(self.logging_modules))
		endpoint.add_listener(self.write)
		self.endpoints.append(endpoint)

	def write(self, packet):
		relative_timestamp = DtypeConverter.int_to_bin(packet.timestamp - self.start_time)
		module_id = DtypeConverter.char_to_bin(packet.module_id)
		self.log_file.write(packet.binary + relative_timestamp + module_id)

	def to_json(self, dictionary):
		return json.dumps(dictionary, sort_keys=True, indent='\t')

	def dispose(self):
		for endpoint in self.endpoints:
			self.assign_module_id(endpoint, -1)
			endpoint.remove_listener(self.write)
		self.logging_modules = {}
		self.endpoints = []
		self.log_modules.close()
		self.log_file.close()
		self.config_file.close()
		self.meta_file.close()
		print('DataWriter session ended')

	def end_session(self):
		self.log_modules.write(self.to_json(self.logging_modules))
		self.config_file.write(self.to_json(self.config))
		self.meta_file.write(self.to_json(self.meta))
		self.dispose()


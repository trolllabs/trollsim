"""
.. module:: misc

The misc module contains a collection of smaller tools which does not
fit any of the other categories (endpoints, protocols, processors,
patterns etc...)
"""

import struct, json, argparse, sys, logging, os


class ArgparseHelper(argparse.ArgumentParser):
	"""
	Prints help when flags or program arguments are set incorrectly.
	"""
	def error(self, message):
		sys.stderr.write('error: %s\n' % message)
		self.print_help()
		sys.exit(2)


def unhandled_exception_callback(e_type, e_value, e_traceback):
	"""
	Handler for unhandled exceptions.

	Logs all unhandled exceptions.
	"""
	if issubclass(e_type, KeyboardInterrupt):
		sys.__excepthook__(e_type, e_value, e_traceback)
	else:
		logging.exception('Uncaught exception', exc_info=(e_type, e_value, e_traceback))


def load_configs(args):
	with open(args.config, 'r') as f:
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
	"""
	Parses a metadata file into dictionary.

	The metadata file is expected to have the following format:

	id;name;dtype

	where:
	- id denotes packet id (unsigned char or 1 byte uint)
	- name is the data channel name (str)
	- dtype is expected datatype (str)

	:param f: A file object with the path to metadata.
	:type f: file object

	:return: metadata, a dict where id and name is one-to-one, and both
	are keywords.
	"""
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
	"""
	Not yet fully used, but a ready instantiated struct packer/unpacker.
	"""
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
	"""
	Write all data to binary file. Each entry should be in
	big-endian. Name of file is the unix timestamp on system when
	program start up.

	The following is logged per session:
	- **log.bin**: The actual log, in binary.
	- **modules.json**: A lookup for module ids and module name.
	- **config.json**: A copy of the config.json used in a logging session.
	- **metadata.json**: Metadata in its JSON form, the same as the one used in a logging session.
	"""
	def __init__(self, config, meta, path='.'):
		"""
		:param config: From config.json, contains all connection headers.
		:param meta: metadata.txt in its parsed form.
		:param path: The directory to write all logdata in.

		:type config: dict
		:type meta: dict
		:type path: str
		"""
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
		"""
		Set a module ID if it has not been set yet.

		:param endpoint: An endpoint (ObservableComponent) object.
		:param module_id: ID to assign the endpoint

		:type endpoint: ObservableComponent
		:type module_id: int
		"""
		if endpoint.name in self.logging_modules:
			endpoint.id = self.logging_modules[endpoint.name]
		else:
			endpoint.id = module_id
			self.logging_modules[endpoint.name] = endpoint.id

	def add_endpoint(self, endpoint):
		"""
		Subscribe to endpoint (ObservableComponent) in order to log its
		data.

		:param endpoint: The endpoint to start logging
		:type endpoint: ObservableComponent
		"""
		self.assign_module_id(endpoint, len(self.logging_modules))
		endpoint.add_listener(self.write)
		self.endpoints.append(endpoint)

	def write(self, packet):
		"""
		Append packet data to log file.
		Logs binary value, timestamp and module id per packet entry.

		:param packet: A TrollPacket from endpoint.
		:type packet: TrollPacket
		"""
		relative_timestamp = DtypeConverter.int_to_bin(packet.timestamp - self.start_time)
		module_id = DtypeConverter.char_to_bin(packet.module_id)
		self.log_file.write(packet.binary + relative_timestamp + module_id)

	def to_json(self, dictionary):
		return json.dumps(dictionary, sort_keys=True, indent='\t')

	def dispose(self):
		"""
		Properly close all (file) objects upon closing.
		"""
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
		"""
		Write all JSON configurations to file before closing.
		"""
		self.log_modules.write(self.to_json(self.logging_modules))
		self.config_file.write(self.to_json(self.config))
		self.meta_file.write(self.to_json(self.meta))
		self.dispose()


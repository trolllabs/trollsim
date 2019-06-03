import json, struct
import numpy as np
from pandas import DataFrame
from collections import defaultdict
from tqdm import tqdm
from os.path import getsize


type_lookup = {
		'float': 'f',
		'int': 'i',
		'uint32': 'I',
		float: 'f',
		int: 'i'
		}


def reverse_dict(d):
	'''
	Retard function
	'''
	return dict(map(reversed, d.items()))


def get_packet_val(meta, packet_id, bin_val):
	packet_type = type_lookup[meta['ids'][packet_id]['type']]
	return struct.unpack('>%s' % packet_type, bin_val)[0]


def entry_generator(path, entry_bytesize):
	with open(path, 'rb') as f:
		eof = False
		while not eof:
			entry = f.read(entry_bytesize)
			if entry and len(entry) == entry_bytesize:
				yield entry
			else:
				#print('%s + EOF' % entry)
				eof = True


def load_trollsim_log(logdir_path):
	'''
	Each entry in TrollSim log is 10 bytes big.
	Byteno.  Meta
	1        ID
	2-5      Value
	6-9      Timestamp
	10       ID of module origin
	'''
	entry_size = 10
	logpath = logdir_path + '/log.bin'
	num_entries = int(getsize(logpath)/entry_size)
	log_entries = entry_generator(logpath, entry_size)
	#logdict = defaultdict(list)
	logdict = {
			'Timestamp': [],
			'Origin': [],
			'Name': [],
			'Value': [],
			'Origin ID': [],
			'Packet ID': [],
			'Channel': []
			}

	with open(logdir_path + '/metadata.json', 'r') as f:
		metadata = json.load(f)
	with open(logdir_path + '/modules.json', 'r') as f:
		modules = reverse_dict(json.load(f))

	print('Loading log into a dictionary..')

	# DELETE
	#counter = 0
	#partition= 6
	#for entry in tqdm(log_entries, total=int(num_entries/partition)):
	#	counter += 1
	#	if counter == int(num_entries/partition):
	#		break
	# DELETE STOP, UNCOMMENT BELOW
	for entry in tqdm(log_entries, total=num_entries):
		packet_id = str(entry[0])

		logdict['Packet ID'].append(entry[0])
		logdict['Timestamp'].append(struct.unpack('>i', entry[5:9])[0])
		logdict['Origin ID'].append(entry[-1])
		logdict['Origin'].append(modules[entry[-1]])
		logdict['Value'].append(get_packet_val(metadata, packet_id, entry[1:5]))
		logdict['Name'].append(metadata['ids'][packet_id]['name'])
		logdict['Channel'].append(logdict['Origin'][-1] + ':' + logdict['Name'][-1])

	return DataFrame(logdict)

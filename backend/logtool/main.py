import sys, struct
from time import sleep
from tqdm import tqdm
from bokeh.io import curdoc
from bokeh.plotting import figure, output_file, show
from bokeh.layouts import row, grid


type_lookup = {
		'float': 'f',
		'int': 'i',
		float: 'f',
		int: 'i'
		}


def metadata_parser(path):
	with open(path, 'r') as f:
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


def entry_generator(path, entry_bytesize):
	with open(path, 'rb') as f:
		eof = False
		while not eof:
			entry = f.read(entry_bytesize)
			if entry and len(entry) == entry_bytesize:
				yield entry
			else:
				print('%s + EOF' % entry)
				eof = True


def append_time_val(datapoints, time, val):
	retval = datapoints
	retval['x'].append(time)
	retval['y'].append(val)
	return retval


def get_packet_val(meta, packet_id, bin_val):
	packet_type = type_lookup[meta['ids'][packet_id]['type']]
	return struct.unpack('>%s' % packet_type, bin_val)[0]


def get_packet_ts(bin_ts):
	return struct.unpack('>i', bin_ts)[0]


sysargs = sys.argv
metadata = metadata_parser('metadata.txt')
if len(sysargs) == 2:
	log = entry_generator(sys.argv[1], 9)
	channels = {}
	figures = [[]]
	print('Loading channels..')
	for entry in tqdm(log):
		packet_id = str(entry[0])
		packet_val = get_packet_val(metadata, packet_id, entry[1:5])
		packet_ts = get_packet_ts(entry[5:])
		channel = channels.get(packet_id, None)
		if not channel:
			channel = {
					'name': metadata['ids'][packet_id]['name'],
					'x': [],
					'y': []
					}
		channels[packet_id] = append_time_val(channel, packet_ts, packet_val)
	print('Done loading. Generating plots..')
	row = 0
	for channel in channels:
		if len(figures[row]) == 4:
			figures.append([])
			row += 1
		new_fig = figure(width=350, height=350, title='%s:%s' % (channel, channels[channel]['name']))
		new_fig.line(channels[channel]['x'], channels[channel]['y'])
		figures[row].append(new_fig)

	# For generating html file
	output_file('%s.html' % sys.argv[1])
	show(grid(figures))

	# For serving plots from web server
	#curdoc().add_root(grid(figures))

else:
	print('Missing logpath argument')


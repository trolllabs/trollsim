import sys, struct, json
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


def reverse_dict(d):
	'''
	Retard function
	'''
	return dict(map(reversed, d.items()))


path = sys.argv[1]
metadata = json.load(open(path + '/metadata.json', 'r'))
modules = reverse_dict(json.load(open(path + '/modules.json', 'r')))
print(modules)
log = entry_generator(path + '/log.bin', 10)
channels = {}
figures = [[]]
print('Loading channels..')
for entry in tqdm(log):
	packet_id = str(entry[0])
	packet_val = get_packet_val(metadata, packet_id, entry[1:5])
	packet_ts = get_packet_ts(entry[5:9])
	packet_module = str(entry[-1])
	channel_id = '%s;%s' % (packet_id, packet_module)
	channel = channels.get(channel_id, None)
	if not channel:
		channel = {
				'name': metadata['ids'][packet_id]['name'],
				'x': [],
				'y': []
				}
	channels[channel_id] = append_time_val(channel, packet_ts, packet_val)
print('Done loading. Generating plots..')
row = 0
for channel in channels:
	if len(figures[row]) == 4:
		figures.append([])
		row += 1
	channel_id, channel_origin = channel.split(';')
	new_fig = figure(width=350, height=350, title='%s:%s, module: %s' % (channel_id, channels[channel]['name'], modules[int(channel_origin)]))
	new_fig.line(channels[channel]['x'], channels[channel]['y'])
	figures[row].append(new_fig)

# For generating html file
output_file('%s.html' % sys.argv[1])
show(grid(figures))

# For serving plots from web server
#curdoc().add_root(grid(figures))

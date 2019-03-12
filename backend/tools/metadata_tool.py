import sys, json

# TODO: integrity check
def main():
	with open(sys.argv[1], 'r') as f:
		metadata = {'ids': {}, 'names': {}}
		for line in f:
			line = line.strip().split(';')
			if (line[0] in metadata['ids'] or line[1] in metadata['names']):
				print('Warning: overlapping entry on id %s or name "%s"' % (line[0], line[1]))
			metadata['ids'][line[0]] = {
					'name': line[1],
					'type': line[2]
					}
			metadata['names'][line[1]] = {
					'id': line[0],
					'type': line[2]
					}

		json.dump(
				metadata,
				open('metadata.json', 'w'),
				sort_keys=True,
				indent='\t'
				)


if __name__ == '__main__':
	main()

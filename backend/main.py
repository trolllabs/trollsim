import sys, logging, threading, json, argparse
from misc import metadata_parser
from endpoints import XPlane, WebUI, Glove, iMotions
from processors import GloveMultiplier, PlatformWriter, DataWriter, DREFTunnel


class ArgparseHelper(argparse.ArgumentParser):
	def error(self, message):
		sys.stderr.write('error: %s\n' % message)
		self.print_help()
		sys.exit(2)


parser = ArgparseHelper()
parser.add_argument('-f','--file', type=str, default='config.json',
		help='Set the path of config file. Default is config.json in working directory.')
parser.add_argument('-m','--meta', type=str, default='metadata.txt',
		help='Set the path of metadata file. Default is metadata.txt in working directory.')
parser.add_argument('-s', '--save', action='store_true', default=False,
		help='Save current session to a logfile.') # Specify where it will be written
args = parser.parse_args()


def load_configs(args):
	with open(args.file, 'r') as f:
		component_config = json.load(f)
	metadata_config = metadata_parser(args.meta)
	return component_config, metadata_config
	return {'component': component_config, 'metadata': metadata_config}


def run_threads(threads):
	for thread in threads:
		thread.start()

	# Wait for threads to terminate
	for thread in threads:
		thread.join()


def main():
	# Define headers.
	logging.basicConfig(level=logging.DEBUG, filename='log.txt')
	config, meta = load_configs(args)
	threads = []

	xplane = XPlane(config['xplane'], meta)
	web = WebUI(config['frontend'], meta)
	glove = Glove(config['glove'], meta)
	imotions = iMotions(config['imotions'], meta)

	threads.append(xplane)
	threads.append(web)
	threads.append(glove)
	threads.append(alarmbox)
	threads.append(imotions)

	gm = GloveMultiplier(glove, web, xplane)
	dt = DREFTunnel(xplane, web)
	logger = DataWriter(xplane)


	run_threads(threads)


if __name__ == "__main__":
	main()


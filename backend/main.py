import sys, logging, json, argparse
from control import ControlAPI
from misc import metadata_parser
from patterns import ModuleFactory
from endpoints import XPlane, WebUI, Arduino, iMotions, AudioSocket
from http.server import HTTPServer


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
	with open(args.meta, 'r') as f:
		metadata_config = metadata_parser(f)
	return component_config, metadata_config


def run(modules):
	api = ControlAPI(modules)
	port = 5050
	server = HTTPServer(('0.0.0.0', port), api)
	print('HTTPServer on port %s' % port)
	server.serve_forever()


def main():
	# Define headers.
	logging.basicConfig(level=logging.DEBUG, filename='log.txt')
	config, meta = load_configs(args)
	modules = ModuleFactory(config, meta)

	modules.new_module('xplane', XPlane)
	modules.new_module('frontend', WebUI)
	modules.new_module('glove', Arduino)
	modules.new_module('alarmbox', Arduino)
	modules.new_module('imotions', iMotions)
	modules.new_module('audiosocket', AudioSocket)

	run(modules)


if __name__ == "__main__":
	main()


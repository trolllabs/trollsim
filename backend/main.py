from control import ControlAPI
from misc import metadata_parser, ArgparseHelper, load_configs
from patterns import ModuleFactory
from endpoints import XPlane, WebUI, Arduino, iMotions, TCPSocket
from processors import GloveMultiplier, AudioTrigger, ControlTrigger
from datastructures import TrollPacket
from http.server import HTTPServer


parser = ArgparseHelper()
parser.add_argument('-f','--file', type=str, default='config.json',
		help='Set the path of config file. Default is config.json in working directory.')
parser.add_argument('-m','--meta', type=str, default='metadata.txt',
		help='Set the path of metadata file. Default is metadata.txt in working directory.')
parser.add_argument('-s', '--save', action='store_true', default=False,
		help='Save current session to a logfile.') # Specify where it will be written
args = parser.parse_args()


def run(modules):
	api = ControlAPI(modules)
	port = 5050
	server = HTTPServer(('0.0.0.0', port), api)
	print('HTTPServer on port %s' % port)
	server.serve_forever()


def main():
	config, meta = load_configs(args)
	modules = ModuleFactory(config)
	TrollPacket.meta = meta

	modules.new_module('xplane', XPlane)
	modules.new_module('frontend', WebUI)
	modules.new_module('glove', Arduino)
	modules.new_module('alarmbox', Arduino)
	modules.new_module('imotions', iMotions)
	modules.new_module('audiosocket', TCPSocket)
	modules.new_module('alarmbox-slave', Arduino)
	modules.new_module('control-socket', TCPSocket)
	modules.new_module('audio-control', Arduino)
	modules.new_processor('gm', GloveMultiplier)
	modules.new_processor('at', AudioTrigger)
	modules.new_processor('ct', ControlTrigger)

	run(modules)


if __name__ == "__main__":
	import sys, logging
	from misc import unhandled_exception_callback
	log_format = '%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s'
	log_formatter = logging.Formatter(log_format)

	consoleHandler = logging.StreamHandler()
	consoleHandler.setFormatter(log_formatter)

	fileHandler = logging.FileHandler('error_log.txt')
	fileHandler.setFormatter(log_formatter)

	error_logger = logging.getLogger()
	error_logger.addHandler(consoleHandler)
	error_logger.addHandler(fileHandler)

	sys.excepthook = unhandled_exception_callback

	try:
		main()
	except KeyboardInterrupt:
		print('Goodbye')


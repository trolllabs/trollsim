import sys, logging, threading, json, argparse
from endpoints import UDPClient, UDPServer, TCPServer, Arduino, ObservableData
from processors import GloveMultiplier, PlatformWriter


class ArgparseHelper(argparse.ArgumentParser):
	def error(self, message):
		sys.stderr.write('error: %s\n' % message)
		self.print_help()
		sys.exit(2)


parser = ArgparseHelper()
parser.add_argument('-f','--file', type=str, default='config.json',
		help='Set the path of config file. Default is config.json in working directory.')
args = parser.parse_args()


def main():
	# Define headers.
	logging.basicConfig(level=logging.DEBUG, filename='log.txt')
	threads = []

	with open(args.file, 'r') as f:
		config = json.load(f)
	xplane_config = config['xplane']
	xplane_config = config['xplane']
	frontend_config = config['frontend']
	arduino_config = config['arduino']

	# Initialize local endpoints and also connecting to external endpoints
	xplane_writesocket = UDPClient(xplane_config['write']['ip'], xplane_config['write']['port'])
	xplane_readsocket = UDPServer(xplane_config['read']['ip'], xplane_config['read']['write'])
	frontend_socket = TCPServer(frontend_config['ip'], frontend_config['port'])
	glove_arduino = Arduino(arduino_config['glove'], 115200)
	ehealth_arduino = Arduino(arduino_config['ehealth'], 115200)
	platform_arduino = Arduino(arduino_config['platform'], 115200)


	# Initialize processing logic and connect internal endpoints
	glove_processor = GloveMultiplier(glove_arduino, frontend_socket, xplane_writesocket)
	platform = PlatformWriter(xplane_readsocket, platform_arduino)

	# Initialize new threads for datareading components
	threads.append(glove_arduino())
	threads.append(ehealth_arduino())
	threads.append(frontend_socket())
	threads.append(xplane_readsocket())
	threads.append(platform_arduino())

	# Wait for threads to terminate (will never happen)
	for thread in threads:
		thread.join()


if __name__ == "__main__":
	main()


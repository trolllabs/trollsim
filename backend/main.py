import sys, logging, threading
from endpoints import UDPClient, UDPServer, TCPServer, Arduino, ObservableData
from processors import GloveMultiplier, PlatformWriter


def main():
	# Define headers. TODO argparse later
	logging.basicConfig(level=logging.DEBUG, filename='log.txt')
	xplane_ip = '10.53.25.98'
	xplane_port = 49000
	frontend_ip = 'localhost'
	frontend_port = 8005
	glove_sn = 'AH03J54W'
	ehealth_sn = '7533832353535140E1C2'
	platform_sn = '85439303133351D0B002'
	threads = []

	# Initialize components, and also connecting to external endpoints
	xplane_writesocket = UDPClient(xplane_ip, xplane_port)
	xplane_readsocket = UDPServer('0.0.0.0', xplane_port)
	frontend_socket = TCPServer(frontend_ip, frontend_port)
	glove_arduino = Arduino(glove_sn, 115200)
	ehealth_arduino = Arduino(ehealth_sn, 115200)
	platform_arduino = Arduino(platform_sn, 115200)

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


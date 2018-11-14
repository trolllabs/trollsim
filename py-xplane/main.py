import sys, logging, threading
from readers import ArduinoReader, SocketReader
from tools.networking import udp_server, UDPClient, TCPServer
from processors import GloveMultiplier, FrontendSocket


def main():
	logging.basicConfig(level=logging.DEBUG, filename='log.txt')
	xplane_ip = '10.53.25.98'
	xplane_port = 49000
	frontend_ip = 'localhost'
	frontend_port = 8005
	glove_ports = ['/dev/ttyUSB1', '/dev/ttyUSB2']
	ehealth_ports = ['/dev/ttyACM0']

	xplane_socket = UDPClient(xplane_ip, xplane_port)
	frontend_socket = TCPServer(frontend_ip, frontend_port)

	ehealth_reader = ArduinoReader(ehealth_ports, 115200)
	glove_reader = ArduinoReader(glove_ports, 115200)
	frontend_reader = SocketReader(frontend_socket.read)
	xplane_reader = SocketReader(xplane_socket.read)

	glove_processor = GloveMultiplier(xplane_socket.send, glove_reader, frontend_reader)
	frontend = FrontendSocket(
			glove_processor.frontend_handler,
			frontend_socket.send,
			frontend_reader,
			glove_reader)

	frontend_reader()
	xplane_reader()
	ehealth_reader()
	glove_reader()


	# Very temporary solution
	from time import sleep
	sleep(2**63/10**9-1)


if __name__ == "__main__":
	main()


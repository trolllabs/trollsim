import sys, logging, threading
from readers import ArduinoReader, SocketReader
from processors import GloveMultiplier, FrontendSocket
from endpoints import UDPClient, UDPServer, TCPServer, Arduino


def main():
	logging.basicConfig(level=logging.DEBUG, filename='log.txt')
	xplane_ip = '10.53.25.98'
	xplane_port = 49000
	frontend_ip = 'localhost'
	frontend_port = 8005
	glove_sn = 'AH03J54W'
	ehealth_sn = '7533832353535140E1C2'

	xplane_socket = UDPClient(xplane_ip, xplane_port)
	frontend_socket = TCPServer(frontend_ip, frontend_port)
	glove_arduino = Arduino(glove_sn, 115200)
	ehealth_arduino = Arduino(ehealth_sn, 115200)

	glove_reader = ArduinoReader(glove_arduino.read)
	ehealth_reader = ArduinoReader(ehealth_arduino.read)
	frontend_reader = SocketReader(frontend_socket.read)
	xplane_reader = SocketReader(xplane_socket.read)

	glove_processor = GloveMultiplier(glove_reader, frontend_reader, xplane_socket.send)
	frontend = FrontendSocket(
			glove_processor.frontend_handler,
			frontend_reader,
			glove_reader,
			frontend_socket.send)

	glove_reader()
	ehealth_reader()
	frontend_reader()
	xplane_reader()


	# Very temporary solution
	from time import sleep
	sleep(2**63/10**9-1)


if __name__ == "__main__":
	main()


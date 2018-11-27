import sys, logging, threading
from endpoints import UDPClient, UDPServer, TCPServer, Arduino, ObservableData
from processors import GloveMultiplier, FrontendSocket, PlatformWriter


def main():
	logging.basicConfig(level=logging.DEBUG, filename='log.txt')
	xplane_ip = '10.53.25.98'
	xplane_port = 49000
	frontend_ip = 'localhost'
	frontend_port = 8005
	glove_sn = 'AH03J54W'
	ehealth_sn = '7533832353535140E1C2'
	platform_sn = '85439303133351D0B002'

	xplane_writesocket = UDPClient(xplane_ip, xplane_port)
	xplane_readsocket = UDPServer('0.0.0.0', xplane_port)
	frontend_socket = TCPServer(frontend_ip, frontend_port)
	glove_arduino = Arduino(glove_sn, 115200)
	ehealth_arduino = Arduino(ehealth_sn, 115200)
	platform_arduino = Arduino(platform_sn, 115200)

	glove_reader = ObservableData(glove_arduino.read)
	ehealth_reader = ObservableData(ehealth_arduino.read)
	frontend_reader = ObservableData(frontend_socket.read)
	xplane_reader = ObservableData(xplane_readsocket.read)

	platform_reader = ObservableData(platform_arduino.read) # debug only

	glove_processor = GloveMultiplier(glove_reader, frontend_reader, xplane_writesocket.send)
	frontend = FrontendSocket(
			glove_processor.frontend_handler,
			frontend_reader,
			glove_reader,
			frontend_socket.send)
	platform = PlatformWriter(xplane_reader, platform_arduino.send, platform_reader)

	glove_reader()
	ehealth_reader()
	frontend_reader()
	xplane_reader()
	platform_reader()


	# Very temporary solution
	from time import sleep
	sleep(2**63/10**9-1)


if __name__ == "__main__":
	main()


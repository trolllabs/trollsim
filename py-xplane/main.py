import socket, sys
from frontend.frontend_socket import FrontendSocket
from data_readers.arduino_reader import ArduinoReader
from tools.networking import udp_server, UDPClient
from tools.xplane_variables import *
from data_processors.xplane_processor import XPlaneConnector
from _thread import start_new_thread


def main():
	local_ip = '0.0.0.0'
	xplane_ip = '10.53.25.98'
	xplane_port = 49000
	arduino_ports = ['/dev/ttyUSB1', '/dev/ttyUSB2']

	xp_adapter = XPlaneConnector(expected_reading)
	xplane_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	frontend_sock = FrontendSocket(('localhost', 8005), xp_adapter.frontend_handler).run()
	data_reader = ArduinoReader(arduino_ports, 115200)

	xp_adapter(data_reader.read(), UDPClient(xplane_ip, xplane_port).send)
	#udp_server(sock, (local_ip, xplane_port))


if __name__ == "__main__":
	main()


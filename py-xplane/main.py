import socket, sys
from frontend.frontend_socket import FrontendSocket
from xplane.arduino_reader import ArduinoReader
from xplane.networking import XPlaneConnector, udp_client, udp_server
from xplane.xp_vars import *
from _thread import start_new_thread


def main():
	arduino_ports = ['/dev/ttyUSB1', '/dev/ttyUSB2']

	xp_adapter = XPlaneConnector()
	xplane_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	frontend_sock = FrontendSocket(('localhost', 8005), xp_adapter.frontend_handler).run()

	local_ip = '0.0.0.0'
	destination_ip = '192.168.1.136'
	port = 49000
	data_reader = ArduinoReader(arduino_ports, 115200)

	udp_client(
			xplane_sock,
			(destination_ip, port),
			xp_adapter.wrap(data_reader.read(), expected_reading)
			)
	#udp_server(sock, (local_ip, port))


if __name__ == "__main__":
	main()


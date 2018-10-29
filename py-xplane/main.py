import socket, sys
from frontend.frontend_socket import FrontendSocket
from xplane.arduino_reader import ArduinoReader
from xplane.networking import XPlaneConnector, udp_client, udp_server
from xplane.xp_vars import *
from _thread import start_new_thread


def main():
	xp_adapter = XPlaneConnector()
	xplane_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	frontend_sock = FrontendSocket(('localhost', 8005), xp_adapter.frontend_handler).run()
	data_reader = ArduinoReader('/dev/ttyUSB1', 115200)

	local_ip = '0.0.0.0'
	destination_ip = '192.168.1.136'
	port = 49000

	udp_client(
			xplane_sock,
			(destination_ip, port),
			xp_adapter.wrap(data_reader.read(), expected_reading)
			)
	#udp_server(sock, (local_ip, port))


if __name__ == "__main__":
	main()


import socket, sys
from frontend.frontend_socket import FrontendSocket
from xplane.arduino_reader import ArduinoReader
from xplane.networking import udp_client, udp_server
from xplane.xplane_processor import XPlaneConnector
from xplane.xp_vars import *
from _thread import start_new_thread


def main():
	local_ip = '0.0.0.0'
	xplane_ip = '10.53.25.98'
	xplane_port = 49000
	arduino_ports = ['/dev/ttyUSB1', '/dev/ttyUSB2']

	xp_adapter = XPlaneConnector()
	xplane_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	frontend_sock = FrontendSocket(('localhost', 8005), xp_adapter.frontend_handler).run()
	data_reader = ArduinoReader(arduino_ports, 115200)

	udp_client(
			xplane_sock,
			(xplane_ip, xplane_port),
			xp_adapter.wrap(data_reader.read(), expected_reading)
			)
	#udp_server(sock, (local_ip, xplane_port))


if __name__ == "__main__":
	main()


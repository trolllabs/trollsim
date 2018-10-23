import socket, sys
from xplane.arduino_reader import ArduinoReader
from xplane.networking import XPlaneDataAdapter, udp_client, udp_server
from xplane.xp_vars import *


def main():
	xp_adapter = XPlaneDataAdapter()
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	mc_reader = ArduinoReader('/dev/ttyUSB2', 115200)

	local_ip = '0.0.0.0'
	destination_ip = '192.168.1.136'
	port = 49000

	udp_client(
			sock,
			(destination_ip, port),
			xp_adapter.wrap(mc_reader.read(), expected_reading)
			)
	#udp_server(sock, (local_ip, port))


if __name__ == "__main__":
	main()


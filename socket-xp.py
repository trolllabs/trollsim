import socket, sys, struct
from time import sleep


def create_dref_packet(header, value, name):
	packer = struct.Struct('%ds f %ds' % (len(header), len(name)))
	vals = ((header + '\0').encode(), value, name.encode())
	return packer.pack(*vals)

def udp_server(udp_sock, address):
	try:
		print('Binding..')
		udp_sock.bind(address)
		print('UDP: Listening to %s %s' % address)
		while True:
			data, addr = udp_sock.recvfrom(1024)
			print(data.hex().upper())
	except socket.error as e:
		sys.stderr.write('Socket Error: %s' % str(e))
	except Exception as e:
		sys.stderr.write('Error: %s' % str(e))
	finally:
		sock.close()
		print('Socket closed')
		sys.exit(0)


def udp_client(udp_sock, address):
	header = 'DREF'
	value = 4.0
	name = 'sim/test/test_float'
	message = create_dref_packet(header, value, name)
	print(message)
	while True:
		udp_sock.sendto(message, address)
		sleep(1)



local_ip = '0.0.0.0'
destination_ip = '10.24.11.21'
port = 49000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_client(sock, (destination_ip, port))
#udp_server(sock, (local_ip, port))

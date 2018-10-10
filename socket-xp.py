import socket, sys, struct
from time import sleep


def float_to_hex(f):
	return hex(struct.unpack('<I', struct.pack('<f', f))[0])

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
	value = float_to_hex(3.0)
	name = 'sim/test/test_float'
	message = '%s\0%s%s' % (header, value, name)
	message = '%e' % 3.0
	while True:
		print(message)
		udp_sock.sendto(message.encode(), address)
		sleep(1)


ip = '0.0.0.0'
port = 49000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_client(sock, ('localhost', port))
#udp_server(sock, (ip, port))

import socket, sys, struct


def null_terminate(s):
	return s + '\0'


def create_dref_packet(header, value, name):
	header = null_terminate(header)
	name = null_terminate(name)
	pad_length = 509 - (len(header) + 4 + len(name))
	pad = '\0'*pad_length
	packer = struct.Struct('<%ds f %ds %ds' % (len(header), len(name), pad_length))
	vals = (header.encode(), value, name.encode(), pad.encode())
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
	name = 'sim/test/test_float'
	while True:
		value = float(input('Set new value ~> '))
		message = create_dref_packet(header, value, name)
		udp_sock.sendto(message, address)
		print('send')


local_ip = '0.0.0.0'
destination_ip = '10.24.11.21'
port = 49000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_client(sock, (destination_ip, port))
#udp_server(sock, (local_ip, port))

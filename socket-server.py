import socket, sys


def udp_server(address):
	print('UDP: Listening to %s %s' % address)
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		print('Binding..')
		sock.bind(address)
		print('Ok')
		while True:
			data, addr = sock.recvfrom(4096)
			print(data.decode('utf-8').strip())
	except socket.error as e:
		sys.stderr.write('Error: %s' % str(e))
	finally:
		sock.close()
		print('Socket closed')
		sys.exit(0)


address = 'localhost'
port = 49000

udp_server((address, port))

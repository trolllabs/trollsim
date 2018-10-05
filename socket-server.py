import socket, sys


def udp_server(address):
	print('UDP: Listening to %s %s' % address)
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		print('Binding..')
		sock.bind(address)
		print('Ok')
		while True:
			data, addr = sock.recvfrom(1024)
			print(data.hex().upper())
	except socket.error as e:
		sys.stderr.write('Socket Error: %s' % str(e))
	except Exception as e:
		sys.stderr.write('Error: %s' % str(e))
	finally:
		sock.close()
		print('Socket closed')
		sys.exit(0)


address = '0.0.0.0'
port = 49000

udp_server((address, port))

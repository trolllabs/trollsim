import socket, sys


def udp_server(udp_sock, address):
	try:
		print('Binding..')
		udp_sock.bind(address)
		print('UDP: Listening to %s %s' % address)
		while True:
			data, addr = udp_sock.recvfrom(1024)
			print(data.hex().upper())
	except socket.error as e:
		sys.stderr.write('Socket Error: %s\n' % str(e))
	except Exception as e:
		sys.stderr.write('Error: %s\n' % str(e))
	finally:
		sock.close()
		print('Socket closed')
		sys.exit(0)


def udp_client(udp_sock, address, message_generator):
	messages = message_generator()
	for message in messages:
		#print(message.hex())
		udp_sock.sendto(message, address)


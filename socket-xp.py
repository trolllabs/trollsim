import socket, sys, struct, logging, serial
from time import sleep


def null_terminate(s):
	return s + '\0'


def create_null_pad(pad_length):
	return = ('\0'*pad_length).encode()


def create_dref_packet(value, name):
	header = null_terminate('DREF')
	name = null_terminate(name)
	pad_length = 509 - (len(header) + 4 + len(name))
	pad = create_null_pad(pad_length)

	packer = struct.Struct('<%ds f %ds %ds' % (len(header), len(name), pad_length))
	return packer.pack(*(header.encode(), value, name.encode(), pad.encode()))


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
	name = 'sim/test/test_float'
	while True:
		value = float(input('Set new value ~> '))
		message = create_dref_packet(value, name)
		udp_sock.sendto(message, address)
		print('send')


def main():
	#arg = sys.argv[1]
	logging.basicConfig(level=logging.DEBUG, filename='log.txt')
	ser = serial.Serial('/dev/ttyUSB0', 115200)
	error_logs = open('log.txt', 'a')

	local_ip = '0.0.0.0'
	destination_ip = '10.24.11.21'
	port = 49000

	while True:
		try:
			msg = ser.readline().decode('utf-8').split()
			msg = list(map(float, msg))
			print('roll: %s, pitch: %s, yaw: %s' % (msg[0], msg[1], msg[2]))
		except Exception as e:
			sys.stderr.write(str(e))
			logging.exception('Error when reading from serial')

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	udp_client(sock, (destination_ip, port))
	#udp_server(sock, (local_ip, port))


if __name__ == "__main__":
	main()


import serial, struct
from time import sleep
from serial.tools import list_ports


PORT = '/dev/ttyACM0'

port_info = next(list_ports.grep(PORT))
print('Port: %s\nSerial number: %s' % (PORT, port_info.serial_number))
print('=============================================')

s = serial.Serial(PORT, 115200)#, parity=serial.PARITY_EVEN)

'''
Expects:
	byte 1 - sensor id
	byte 2-5 - sensor data
	byte 6 - newline character
	big endianness
'''
while True:
	reading = s.readline()

	if (len(reading) == 6):
		print(reading[:-1])
		sensor_data = reading[1:-1]
		sensor_id = reading[0]
		print(sensor_id, sensor_data.hex().upper())

		# Test float data
		# 0x9EEF8340 test float: 4.123
		# 0x05D4F642 test2 float: 123.4141
		print('struct unpack float:', struct.unpack('>f', sensor_data)[0])

		# Test int32 data
		print('struct unpack int:', struct.unpack('>i', sensor_data)[0])


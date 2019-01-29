import serial, struct
from time import sleep


s = serial.Serial('/dev/ttyACM4', 115200)#, parity=serial.PARITY_EVEN)


'''
Expects:
	byte 1 - sensor id
	byte 2-5 - sensor data
	byte 6 - newline character
'''
while True:
	reading = s.readline()

	if (len(reading) == 6):
		sensor_data = reading[1:-1]
		sensor_id = reading[0]
		print(sensor_id, sensor_data.hex().upper())

		# Test float data
		# 0x9EEF8340 test float: 4.123
		# 0x05D4F642 test2 float: 123.4141
		print('struct unpack', struct.unpack('f', sensor_data)[0])

		# Test int32 data
		print('struct unpack', struct.unpack('i', sensor_data)[0])


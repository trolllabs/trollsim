import serial
import time

ser = serial.Serial('com8',9600) ## MUST BE CHANGED TO THE CORRECT ARDUINO PORT AND DATA TRANSMISSON RATE

#ser.close()
#ser.open()
with open('output.txt', 'w') as f:
    for i in range(0, 20):
        newdata = ser.readline().decode('utf-8')
        print(newdata)
        f.write("%sTime: %s, " % (newdata, int(time.time())))

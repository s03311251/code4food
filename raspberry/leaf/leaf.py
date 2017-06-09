#!/usr/bin/python3
import os
from sense_hat import SenseHat
import serial
#import socket
import subprocess
import threading
import time

class threadReadSerial (threading.Thread):
	def run(self):
		data = {}
		data_flag = ''
		while True :
			#global dht_status
			#global dht_flag
			line = ser.readline().decode('utf-8')[:-2]
			if line:  # If it isn't a blank line
				print(line)

				if line == 'moisture':
					data_flag = 'Moisture'
				elif line == 'light':
					data_flag = 'Light'
				elif line == 'temperature':
					data_flag = 'Temperature'
				elif line == 'humidity':
					data_flag = 'Enviroment Humidity'
				elif line == 'led':
					data_flag = 'LED Intensity'
				elif data_flag != '':
					data[data_flag] = float(line)
					print (data_flag, ':', data[data_flag])
					data_flag = ''		
		

def send_int_to_arduino(int_value):
	empty_bytes = bytes([int(int_value/256)])
	empty_bytes2 = bytes([int_value%256])
	ser.write(empty_bytes)
	ser.write(empty_bytes2)

class photoThread (threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
	def run(self):
		global pwd
		global host
		with open(pwd+'/data_leaf.txt', 'r') as f:
			photo_id = int(f.readline())

		while True:
			photo_id=(photo_id+1)%256
			command = 'avconv -y -f video4linux2 -s 640x480 -i /dev/video0 -ss 0:0:2 -frames 1 ' + pwd + '/data_leaf/' + str(photo_id).zfill(10) + '.jpg 2>/dev/null'
			print ('Taking photo')
			subprocess.call(command, shell=True)

			with open(pwd+'/data_leaf.txt', 'w') as f:
				f.write(str(photo_id))
			'''
			# send photo
			stem = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			stem.connect((host, 8763))
			stem.send(b"r")
			stem.send(bytes([photo_id]))

			print ("Sending photo")
			f = open(pwd+'/data_leaf/' + str(photo_id).zfill(10) + '.jpg','rb')
			l = f.read(1024)
			while (l):
				stem.send(l)
				l = f.read(1024)
			f.close()

			print('Done sending')
			stem.close()
			'''
			time.sleep(10) # 10 sec


sense = SenseHat()
host = "192.168.1.1"
dht_status = 'No data'
dht_flag = 0

pwd = os.getcwd()
print (pwd)

# communicate with Arduino
ser = serial.Serial('/dev/ttyUSB0', 9600)

thread1 = photoThread()
thread1.start()

thread2 = threadReadSerial()
thread2.start()

while True: # data loop
	time.sleep(10) # 10 sec
	'''
	stem = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	'''
	humidity = sense.get_humidity()
	temperature = sense.get_temperature()

	message = "SenseHAT Temperature = "+str(temperature)+" C\nSenseHATHumidity = "+str(humidity)+" %"
	print(message)
	'''
	stem.sendto(message.encode('utf-8'), (host, 8763))
	'''

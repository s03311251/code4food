#!/usr/bin/python3
import os
from sense_hat import SenseHat
import serial
import socket
import subprocess
import threading
import time

class threadReadSerial (threading.Thread):
	def run(self):
		global data
		global data_fresh
		data_flag = ''
		while True :
			try:
				line = ser.readline().decode('utf-8')[:-2]
			except:
				continue

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
					lock.acquire()
					try:
						data[data_flag] = float(line)
						data_fresh[data_flag] = True
						# print (data_flag, ':', data[data_flag])
					finally:
						lock.release()
						data_flag = ''

class threadPhoto (threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
	def run(self):
		global PWD
		global host
		with open(PWD+'/data_leaf.txt', 'r') as f:
			photo_id = int(f.readline())

		while True:
			photo_id=(photo_id+1)%256

			print ('Taking photo')
			command = 'avconv -y -f video4linux2 -s 640x480 -i /dev/video0 -vf "transpose=2,transpose=2" -ss 0:0:2 -frames 1 '+ PWD + '/data_leaf/' + str(photo_id).zfill(10) + '.jpg 2>/dev/null'
			subprocess.call(command ,shell=True)

			with open(PWD+'/data_leaf.txt', 'w') as f:
				f.write(str(photo_id))
			
			# send photo
			try:
				stem = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				stem.connect((host, 8763))
				stem.send(b"r")
				stem.send(bytes([photo_id]))

				print ("Sending photo")
				f = open(PWD+'/data_leaf/' + str(photo_id).zfill(10) + '.jpg','rb')
				l = f.read(1024)
				while (l):
					stem.send(l)
					l = f.read(1024)
				f.close()

				print('Done sending')
				stem.close()
				
				time.sleep(180) # 180 sec
			except:
				time.sleep(180) # 180 sec
				continue
			

class threadLightandSenseHat (threading.Thread):

	def light(self,is_dim):
		# light(-1) for lighten
		global threshold_upper_light
		threshold_upper_light += is_dim * 30

		if is_dim == 1:
			print ('Dim')
		else:
			print ('Lighten')

		# write to Arduino
		ser.write(b'l')
		send_int_to_arduino(threshold_upper_light)

	def run(self):
		# Light
#		leaf = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#		host_leaf = socket.gethostname()
#		print(host_leaf)
#		leaf.bind(('', 8764))
#		leaf.listen(5)

		# SenseHAT
		sense = SenseHat()
		sense.set_rotation(180)
		sense.clear((255,255,255))
		speed = 0.08

		while True:
			# Light
#			print ("Listening")
#			conn, addr = leaf.accept()
#			command = conn.recv(1)
#
#			if command == b"L": # lighten
#				self.light(-1)
#				print('Done requesting for lighten')
#			elif command == b"D": # dim
#				self.light(1)
#				print('Done requesting for dim')
#
#			conn.close()

			# SenseHAT
			for event in sense.stick.get_events():
				if event.action == 'pressed' and event.direction == 'up':
					sense.show_message('M '+str(data['Moisture']), speed, text_colour=(0,0,255))
				if event.action == 'pressed' and event.direction == 'down':
					sense.show_message('L '+str(data['Light']), speed, text_colour=(255,255,0))
				if event.action == 'pressed' and event.direction == 'right':
					sense.show_message('T '+str(data['Temperature']), speed, text_colour=(255,0,0))
				if event.action == 'pressed' and event.direction == 'left':
					sense.show_message('H '+str(data['Enviroment Humidity']), speed, text_colour=(0,255,255))
				if event.action == 'pressed' and event.direction == 'middle':
					sense.show_message('I '+str(data['LED Intensity']), speed, text_colour=(255,255,255))

			sense.clear((255,255,255))



def send_int_to_arduino(int_value):
	empty_bytes = bytes([int(int_value/256)])
	empty_bytes2 = bytes([int_value%256])
	ser.write(empty_bytes)
	ser.write(empty_bytes2)

# Initial Setup

host = '192.168.1.1'
#host = 'localhost'

data = {}
data_fresh = {}
lock = threading.Lock()
ser = serial.Serial('/dev/ttyUSB0', 9600)
threshold_upper_light = 440
THRESHOLD_MOISTURE = 250

PWD = os.getcwd()
print ("PWD: ",PWD)

# Start Threads
thread1 = threadPhoto()
thread1.start()

thread2 = threadReadSerial()
thread2.start()

thread3 = threadLightandSenseHat()
thread3.start()

# Initialize Arduino

time.sleep(5)
ser.write(b'l')
send_int_to_arduino(threshold_upper_light)

# Data and Water Loop
while True:
	
#	humidity = sense.get_humidity()
#	temperature = sense.get_temperature()

	message = ''
	for key, value in data.items():
		message += key + ': ' + str(value) + '\n'

	print(message)

	stem = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	stem.connect((host, 8763))
	stem.send(b"d"+message.encode('utf-8'))
	print('Done sending')
	stem.close()

	if data['Moisture']> THRESHOLD_MOISTURE :
		ser.write(b'w')

	time.sleep(30) # 30 sec

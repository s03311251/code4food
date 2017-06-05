#!/usr/bin/python3
import subprocess
import time
import socket
import threading
from sense_hat import SenseHat
import serial

sense = SenseHat()
host = "192.168.1.1"

dht_status = 'No data'
dht_flag = 0

class thread_read_serial (threading.Thread):
	def run(self):
		while True :
			global dht_status
			global dht_flag
			line = ser.readline().decode('utf-8')[:-2]
			if line:  # If it isn't a blank line
				print(line)

				if dht_flag == 2:
					dht_status = line
					dht_flag -= 1

				elif dht_flag == 1:
					dht_status = dht_status + '\n' + line
					dht_flag -= 1

				if line == 't':
					dht_flag = 2
		
		

def send_int_to_arduino(int_value):
	empty_bytes = bytes([int(int_value/256)])
	empty_bytes2 = bytes([int_value%256])
	ser.write(empty_bytes)
	ser.write(empty_bytes2)

class photoThread (threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
	def run(self):
		with open('/home/pi/raspberry/data_leaf.txt', 'r') as f:
			photo_id = int(f.readline())

		while True:
			global host
			photo_id=(photo_id+1)%256
			command = 'ffmpeg -y -f video4linux2 -s 640x480 -i /dev/video0 -ss 0:0:2 -frames 1 /home/pi/raspberry/data_leaf/' + str(photo_id).zfill(10) + '.jpg'
			subprocess.call(command, shell=True)

			with open('/home/pi/raspberry/data_leaf.txt', 'w') as f:
				f.write(str(photo_id))

			stem = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			stem.connect((host, 8763))
			stem.send(b"r")
			stem.send(bytes([photo_id]))

			print ("Sending photo")
			f = open('/home/pi/raspberry/data_leaf/' + str(photo_id).zfill(10) + '.jpg','rb')
			l = f.read(1024)
			while (l):
				stem.send(l)
				l = f.read(1024)
			f.close()

			print('Done sending')
			stem.close()

			time.sleep(10) # 10 sec

thread1 = photoThread()
thread1.start()

while True: # data loop
	stem = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	
	humidity = sense.get_humidity()
	temperature = sense.get_temperature()

	message = "Temperature = "+str(temperature)+" C\nHumidity = "+str(humidity)+" %"+"DHT Information:\n"+dht_status
	print(message.encode('utf-8'))
	stem.sendto(message.encode('utf-8'), (host, 8763))

	time.sleep(10) # 10 sec

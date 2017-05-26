#!/usr/bin/python3
import subprocess
import time
import socket
import threading
from sense_hat import SenseHat

sense = SenseHat()
host = "192.168.1.1"

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

	message = "Temperature = "+str(temperature)+" C\nHumidity = "+str(humidity)+" %"
	print(message.encode('utf-8'))
	stem.sendto(message.encode('utf-8'), (host, 8763))

	time.sleep(10) # 10 sec

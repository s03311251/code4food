#!/usr/bin/python3
import subprocess
import socket
import threading

message = "No data"

class dataThread (threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
	def run(self):
		global message
		stem = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		host = socket.gethostname()
		stem.bind((host, 8763))

		while True:
			data, addr = stem.recvfrom(1024) # buffer size is 1024 bytes
			message = data.decode('utf-8')
			print (message)



thread1 = dataThread()
thread1.start()

stem = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
print(host)
stem.bind(('', 8763))
stem.listen(5)

with open('/home/pi/raspberry/data_stem.txt', 'r') as f:
	photo_id = int(f.readline())

while True:

	print ("Listening")

	conn, addr = stem.accept()
	command = conn.recv(1)

	if command == b"r": # receive photo from leaf
		photo_id=photo_id+1
		print(int.from_bytes(conn.recv(1), byteorder='big'))
		print("Receiving photo")
		with open('/home/pi/raspberry/data_stem/' + str(photo_id).zfill(10) + '.jpg', 'wb') as f:
			while True:
				data = conn.recv(1024)
				if not data:
					break
				f.write(data)
		f.close()
		print("Done receiving")

		with open('/home/pi/raspberry/data_stem.txt', 'w') as f:
			f.write(str(photo_id))



	elif command == b"p": # send photo to root

		if photo_id == -1:
			print("Error: No photo found")

		else:
			print ("Sending photo")
			f = open('/home/pi/raspberry/data_stem/' + str(photo_id).zfill(10) + '.jpg','rb')
			l = f.read(1024)
			while (l):
				conn.send(l)
				l = f.read(1024)
			f.close()
			print('Done sending')



	elif command == b"v": # send video to root

		if photo_id == -1:
			print('Error: No photo found')

		else:

			# get the correct photo_id
			with open('data_stem.txt', 'r') as f:
				photo_id_end = int(f.readline())

			if photo_id_end == -1:
				print('Error: No photo found')
		
			else:
				print('Making video')

				photo_id_start = photo_id_end - 120 # make last 120 photos into video
				if ( photo_id_start < 0):
					photo_id_start = 0

				# call ffmpeg to make video
				command = 'ffmpeg -y -framerate 10 -start_number '+ str(photo_id_start) +' -i /home/pi/raspberry/data_stem/%10d.jpg -c:v libtheora -r 10 output.ogg' # photo name is 10-digit long
				subprocess.call(command, shell=True)

				# send video
				f = open('output.ogg','rb')
				l = f.read(1024)
				while (l):
					conn.send(l)
					l = f.read(1024)
				f.close()
				print("Done sending")



	elif command == b"d": # send data to root

		conn.send(message.encode('utf-8'))
		print('Done sending')



	else:
		print ("What?")

	conn.close()


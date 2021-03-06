#!/usr/bin/python3
import os
import subprocess
import socket
import threading

PWD = os.getcwd()
print ("PWD: ",PWD)

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



def leaf_command(command):

		leaf = socket.socket()
		host_leaf = '192.168.1.49'
#		host_leaf = 'localhost'
		leaf.connect((host_leaf, 8764))
		leaf.send(command)
		print('Command ' + str(command) + ' sent')
		leaf.close()



thread1 = dataThread()
thread1.start()

stem = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
print(host)
stem.bind(('', 8763))
stem.listen(5)

with open(PWD + '/data_stem.txt', 'r') as f:
	photo_id = int(f.readline())

while True:

	print ("Listening")

	conn, addr = stem.accept()
	command = conn.recv(1)

	if command == b"r": # receive photo from leaf
		photo_id=photo_id+1
		print(int.from_bytes(conn.recv(1), byteorder='big'))
		print("Receiving photo")
		with open(PWD + '/data_stem/' + str(photo_id).zfill(10) + '.jpg', 'wb') as f:
			while True:
				data = conn.recv(1024)
				if not data:
					break
				f.write(data)
		f.close()
		print("Done receiving")

		with open(PWD + '/data_stem.txt', 'w') as f:
			f.write(str(photo_id))



	elif command == b"p": # send photo to root

		if photo_id == -1:
			print("Error: No photo found")

		else:
			print ("Sending photo")
			path = PWD + '/data_stem/' + str(photo_id).zfill(10) + '.jpg'
			print ('Opening ' + path)
			f = open(path, 'rb')
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

				# call avconv to make video

				command = 'avconv -y -framerate 10'

				photo_id_start = photo_id_end - 120 # make last 120 photos into video
				if ( photo_id_start > 0):
					command += ' -start_number '+ str(photo_id_start) 

				command += ' -i '+ PWD + '/data_stem/%10d.jpg -c:v libtheora -r 10 '+ PWD + '/data_stem/output.ogg' # photo name is 10-digit long
				subprocess.call(command, shell=True)

				# send video
				f = open(PWD + '/data_stem/output.ogg','rb')
				l = f.read(1024)
				while (l):
					conn.send(l)
					l = f.read(1024)
				f.close()
				print("Done sending")



	elif command == b"d": # receive data from leaf

		data = conn.recv(1024)
		message = data.decode("utf-8")
		print (message)
		print('Data received')


	elif command == b"s": # send data to root

		conn.send(message.encode('utf-8'))
		print('Done sending')



	elif command == b"L": # lighten
		leaf_command(b"L")
		print('Done requesting for lighten')

	elif command == b"D": # dim
		leaf_command(b"D")
		print('Done requesting for dim')

	elif command == b"w": # water
		leaf_command(b"w")
		print('Done requesting for watering')



	else:
		print ("What?")

	conn.close()


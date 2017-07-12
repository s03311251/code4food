#!/usr/bin/python3
import time
import telepot
import subprocess
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import socket
import csv

chuchuyeah = False

def photo(chat_id):

	# get crop_id
	crop_id = 0;
	with open('crop_list.csv') as f:
		for row in csv.DictReader(f):
			if str(chat_id) == row['user']:
				crop_id = row['id']
				break
	f.close()

	# request photo
	bot.sendMessage(chat_id, "Requesting photo...")

	host = '192.168.100.101'
	stem = socket.socket()
	stem.connect((host, 8763))
	stem.send(b"p")
	print("Requesting photo from "+str(host))

	bot.sendMessage(chat_id, 'Receiving photo...')
	with open( str(crop_id)+'.jpg', 'wb') as f:
		while True:
			data = stem.recv(1024)
			if not data:
				break
			f.write(data)

	f.close()
	stem.close()
	print('Photo Received')

	bot.sendMessage(chat_id, 'Sending photo...')

	print('Opening '+str(crop_id)+'.jpg')

	with open(str(crop_id)+'.jpg', 'rb') as f:
		bot.sendPhoto(chat_id, f)



def video(chat_id):

	bot.sendMessage(chat_id, "Requesting video...")

	host = '192.168.100.101'
	stem = socket.socket()
	stem.connect((host, 8763))
	stem.send(b"v")

	bot.sendMessage(chat_id, 'Receiving video...')
	with open('tmp.ogg', 'wb') as f:
		while True:
			data = stem.recv(1024)
			if not data:
				break
			f.write(data)

	f.close()
	stem.close()
	print('Video Received')

	bot.sendMessage(chat_id, 'Sending video...')

	print('Opening tmp.ogg')

	# send video
	with open('tmp.ogg', 'rb') as f:
		bot.sendVideo(chat_id, f)



def status(chat_id):

	# request
	bot.sendMessage(chat_id, "Requesting data...")

	host = '192.168.100.101'
	stem = socket.socket()
	stem.connect((host, 8763))
	stem.send(b"d")

	bot.sendMessage(chat_id, 'Receiving data...')
	data = stem.recv(1024)
	stem.close()
	print('Data Received')

	datamessage = data.decode('utf-8')
	bot.sendMessage(chat_id, datamessage)



def harvest(chat_id):
	# get crop_id
	crop_id = 0
	crop_name = '?'
	with open('crop_list.csv') as f:
		for row in csv.DictReader(f):
			if str(chat_id) == row['user']:
				crop_id = row['id']
				crop_name = row['type']
				break
	f.close()

	with open('crop_harvested.csv', 'a', newline='') as f:
		spamwriter = csv.writer(f)
		spamwriter.writerow([crop_id, chat_id, crop_name])
	f.close()



def available(chat_id):
	with open('crop_harvested.csv') as f:
		for row in csv.DictReader(f):
			bot.sendMessage(chat_id, row['type'])
	f.close()



def ex(chat_id,crop_name):
	# get crop_id
	crop_id = 0;
	with open('crop_harvested.csv') as f:
		for row in csv.DictReader(f):
			if crop_name == row['type']:
				crop_id = row['id']
				break
	f.close()

	bot.sendMessage(chat_id, 'Crop ID: '+str(crop_id))

	bot.sendMessage(chat_id, 'Sending photo...')

	print('Opening '+str(crop_id)+'.jpg')

	with open(str(crop_id)+'.jpg', 'rb') as f:
		bot.sendPhoto(chat_id, f)

	bot.sendMessage(chat_id, 'To Confirm, please enter: /request (Crop ID)')



def request(chat_id,crop_id):
	owner_id = '0'
	crop_name = '?'
	owner_name = '?'
	owner_address = '?'
	chat_name = '?'
	with open('crop_harvested.csv') as f:
		for row in csv.DictReader(f):
			if crop_id == row['id']:
				owner_id = row['user']
				crop_name = row['type']
				break
	f.close()

	with open('user.csv') as f:
		for row in csv.DictReader(f):
			if str(owner_id) == row['user']:
				owner_name = row['name']
				owner_address = row['address']
			if str(chat_id) == row['user']:
				chat_name = row['name']
	f.close()

	bot.sendMessage(owner_id, chat_name + ' would like to request for your '+crop_name )
	bot.sendMessage(chat_id, 'Request sent')
	bot.sendMessage(chat_id, 'Owner Information:\n'+owner_name+'\n'+owner_address)
	


def register(chat_id,crop_name):

	crop_id = 1
	with open('crop_list.csv') as f:
		for row in csv.DictReader(f):
			crop_id=int((row['id']))
	f.close()

	crop_id2 = 1
	with open('crop_harvested.csv') as f:
		for row in csv.DictReader(f):
			crop_id2=int((row['id']))
	f.close()

	if crop_id2 > crop_id:
		crop_id = crop_id2

	crop_id = crop_id + 1

	with open('crop_list.csv', 'a', newline='') as f:
		spamwriter = csv.writer(f)
		spamwriter.writerow([crop_id, chat_id, crop_name.lower()])

	bot.sendMessage(chat_id, crop_name + ' Registered')



# clear data
def clear(chat_id):
	pass
#	bot.sendMessage(chat_id, 'Delete photos and videos...')
#	subprocess.call('rm data/*', shell=True)
#	with open('data.txt', 'w') as f:
#		f.write('-1')
#	bot.sendMessage(chat_id, 'Done')



def on_chat_message(msg):
	content_type, chat_type, chat_id = telepot.glance(msg)
#	print(content_type, chat_type, chat_id)

# Inline Keyboard
	menu_main = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text='My Crops', callback_data='crop')],
		[InlineKeyboardButton(text='Exchange', callback_data='exchange')],
		# [InlineKeyboardButton(text='My Info', callback_data='info')],
		[InlineKeyboardButton(text='Register Crops', callback_data='register')],
	])

# Read command
	if content_type == 'text':
		command = msg['text'].strip().lower().split()
		if command[0] == '/photo':
			photo(chat_id)

		elif command[0] == '/video':
			video(chat_id)

		elif command[0] == '/status':
			status(chat_id)

		elif command[0] == '/harvest':
			harvest(chat_id)

		elif command[0] == '/ex':
			if len(command) > 1:
				ex(chat_id,command[1])
			else:
				bot.sendMessage(chat_id, 'Please enter: /ex (type of the crop)')

		elif command[0] == '/request':
			if len(command) > 1:
				request(chat_id,command[1])
			else:
				bot.sendMessage(chat_id, 'Please enter: /request (Crop ID)')

		elif command[0] == '/register':
			if len(command) > 1:
				register(chat_id,command[1])
			else:
				bot.sendMessage(chat_id, 'Please enter: /register (type of the crop)')
			
		elif msg['text'].strip().lower() == 'chu chu yeah':
			global chuchuyeah
			if chuchuyeah == False:
				bot.sendMessage(chat_id, 'Please me')
				chuchuyeah = True
			else:
				bot.sendMessage(chat_id, 'Without you')
				chuchuyeah = False

		else:
			bot.sendMessage(chat_id, 'What would you like to do?', reply_markup=menu_main)

	else:
		bot.sendMessage(chat_id, 'What would you like to do?', reply_markup=keyboard)



def on_callback_query(msg):
	query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
#	print('Callback Query:', query_id, from_id, query_data) # -> Callback Query: 637684716986582353 148472543 press

	# define 
	menu_crop = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text='Get Photo', callback_data='photo')],
		[InlineKeyboardButton(text='Get Video', callback_data='video')],
		# [InlineKeyboardButton(text='Lighten', callback_data='lighten')],
		# [InlineKeyboardButton(text='Dim', callback_data='dim')],
		[InlineKeyboardButton(text='Harvest', callback_data='harvest')],
	])

	menu_exchange = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text='Available Crops', callback_data='available')],
		[InlineKeyboardButton(text='Exchange Crops', callback_data='ex')],
		# [InlineKeyboardButton(text='I\'m Feeling Lucky', callback_data='lucky')],
	])

	menu_info = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text='Register Crops', callback_data='register')],
		# [InlineKeyboardButton(text='Clear Photos and Videos', callback_data='clear')],
	])

#	bot.answerCallbackQuery(query_id, text='Got it') # Pop-up message

	# Main Menu
	if query_data == 'crop':
		bot.sendMessage(from_id, 'My Crops', reply_markup=menu_crop)
	if query_data == 'exchange':
		bot.sendMessage(from_id, 'Exchange', reply_markup=menu_exchange)
	if query_data == 'info':
		bot.sendMessage(from_id, 'My Info', reply_markup=menu_info)

	# My Crops
	if query_data == 'photo':
		photo(from_id)
	if query_data == 'video':
		video(from_id)
	if query_data == 'status':
		status(from_id)
	if query_data == 'lighten':
		pass
	if query_data == 'dim':
		pass
	if query_data == 'harvest':
		harvest(from_id)

	# Exchange
	if query_data == 'available':
		available(from_id)
	if query_data == 'ex':
		bot.sendMessage(from_id, 'Please enter: /ex (type of the crop)')
	if query_data == 'lucky':
		pass

	# My Info
	if query_data == 'register':
		bot.sendMessage(from_id, 'Please enter: /register (type of the crop)')
	if query_data == 'clear':
		clear(from_id)


# Main program

bot = telepot.Bot('321380226:AAF6x7YH4uk5fpCtMVdcAKgnd0x_0zWaps4')

bot.message_loop({'chat': on_chat_message, 'callback_query': on_callback_query})
print ('Listening ...')

# Keep the program running.
while 1:
	time.sleep(10)

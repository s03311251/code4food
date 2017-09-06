#!/usr/bin/python3
import os
import time
import telepot
import subprocess
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import socket
import csv
from enum import Enum



def get_id(chat_id):
	user_id = 0
	host = ''
	user_name = ''
	crop_type = ''
	harvested = 'False'
	with open('user_list.csv') as f:
		for row in csv.DictReader(f):
			if str(chat_id) == row['chat_id']:
				user_id = int(row['user_id'])
				host = row['host']
				user_name = row['user_name']
				crop_type = row['crop_type']
				harvested = row['harvested']
				break
	f.close()
	return user_id, host, user_name, crop_type, harvested

	# a,b,c,d,e = func()[[13, 25, 58, 89, 98]]


def photo(chat_id):

	result = get_id(chat_id)
	user_id, host = result[0], result[1]

	# request photo
	bot.sendMessage(chat_id, "Requesting photo...")

	#host = '192.168.100.101'
	#host = 'localhost'
	stem = socket.socket()
	stem.connect((host, 8763))
	stem.send(b"p")
	print("Requesting photo from "+str(host))

	bot.sendMessage(chat_id, 'Receiving photo...')
	with open( PWD + '/data_root/' + str(user_id)+'.jpg', 'wb') as f:
		while True:
			data = stem.recv(1024)
			if not data:
				break
			f.write(data)

	f.close()
	stem.close()
	print('Photo Received')

	bot.sendMessage(chat_id, 'Sending photo...')

	print('Opening '+ PWD + '/data_root/' + str(user_id)+'.jpg')

	with open(PWD + '/data_root/' + str(user_id)+'.jpg', 'rb') as f:
		bot.sendPhoto(chat_id, f)



def video(chat_id):

	result = get_id(chat_id)
	user_id, host = result[0], result[1]

	bot.sendMessage(chat_id, "Requesting video...")

	stem = socket.socket()
	stem.connect((host, 8763))
	stem.send(b"v")

	bot.sendMessage(chat_id, 'Receiving video...')
	with open(PWD + '/data_root/' + str(user_id)+'.ogg', 'wb') as f:
		while True:
			data = stem.recv(1024)
			if not data:
				break
			f.write(data)

	f.close()
	stem.close()
	print('Video Received')

	bot.sendMessage(chat_id, 'Sending video...')

	print('Opening '+ PWD + '/data_root/' + str(user_id)+'.ogg')

	# send video
	with open(PWD + '/data_root/' + str(user_id)+'.ogg', 'rb') as f:
		bot.sendVideo(chat_id, f)



def status(chat_id):

	result = get_id(chat_id)
	host = result[1]

	# request
	bot.sendMessage(chat_id, "Requesting data...")

	stem = socket.socket()
	stem.connect((host, 8763))
	stem.send(b"s")

	bot.sendMessage(chat_id, 'Receiving data...')
	data = stem.recv(1024)
	stem.close()
	print('Data Received')

	datamessage = data.decode('utf-8')
	bot.sendMessage(chat_id, datamessage)



def leaf_command(chat_id, command):

	result = get_id(chat_id)
	host = result[1]

	# request
	stem = socket.socket()
	stem.connect((host, 8763))
	stem.send(command)
	if command == b"D":
		bot.sendMessage(chat_id, "Dim")
		print('Dim')
	elif command == b"L":
		bot.sendMessage(chat_id, "Lighten")
		print('Lighten')
	elif command == b"w":
		bot.sendMessage(chat_id, "Watering")
		print('Watering')
	stem.close()



def harvest(chat_id):

	user_id = 0
	harvested = 0

	# Change a value in CSV
	with open('user_list.csv') as f:
		r = csv.DictReader(f)
		lines = [l for l in r]
	
		for row in lines:
			if str(chat_id) == row['chat_id']:
				user_id = int(row['user_id'])
				if row['harvested'] == 'True':
					bot.sendMessage(chat_id, 'Already harvested')
					f.close()
					return
				row['harvested'] = 'True'
				break
	f.close()

	# Write back
	with open('user_list.csv', 'w') as f:
		w = csv.DictWriter(f, fieldnames = r.fieldnames)
		w.writeheader()
		w.writerows(lines)
	f.close()

	bot.sendMessage(chat_id, 'Successfully harvested')



def available(chat_id):

	crop_set = set()

	with open('user_list.csv') as f:
		for row in csv.DictReader(f):
			if row['crop_type'] != '' and row['harvested'] == 'True':
				crop_set.add(row['crop_type'])
	f.close()

	printstr = ''
	for item in crop_set:
		printstr = printstr + item.title() + '\n'
	bot.sendMessage(chat_id, printstr)



def ex(chat_id,crop_type):

	user_list = []

	with open('user_list.csv') as f:
		for row in csv.DictReader(f):
			if row['harvested'] == 'True' and row['crop_type'] == crop_type:
				user_list.append(row)
	f.close()

#	print (user_list)

	if len(user_list) == 0:
		bot.sendMessage(chat_id, 'Sorry, the crop you entered is not available')
		return False

	else:
		for row in user_list :
			bot.sendMessage(chat_id, 'User ID:' + row['user_id'] + '\n' + 'User Name: ' + row['user_name'])

			bot.sendMessage(chat_id, 'Sending photo...')

			print('Opening ' + PWD + '/data_root/' +row['user_id']+'.jpg')
			with open(PWD + '/data_root/' + row['user_id']+'.jpg', 'rb') as f:
				bot.sendPhoto(chat_id, f)

		bot.sendMessage(chat_id, 'To request the crop, please enter the user ID')
		return True


def request(chat_id, user_id):

	user_name = get_id(chat_id)[2]

	owner_chat_id = 0
	owner_name = ''
	crop_type = ''
	with open('user_list.csv') as f:
		for row in csv.DictReader(f):
			if user_id == row['user_id']:
				owner_chat_id = int(row['chat_id'])
				owner_name = row['user_name']
				crop_type = row['crop_type']
				break
	f.close()

	menu_request = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text='Accept', callback_data='accept '+str(chat_id)+' '+crop_type+' '+owner_name)],
		[InlineKeyboardButton(text='Deny', callback_data='deny '+str(chat_id)+' '+crop_type+' '+owner_name)]
	])

	if owner_chat_id == 0:
		bot.sendMessage(chat_id, 'Error: The user does not exist')
	else:
		bot.sendMessage(owner_chat_id, user_name + ' would like to request for your ' + crop_type + '.\nWould you like to accept the request?', reply_markup=menu_request)
		bot.sendMessage(chat_id, 'Request sent')


def register(chat_id,crop_type):

	# Change a value in CSV
	with open('user_list.csv') as f:
		r = csv.DictReader(f)
		lines = [l for l in r]
	
		for row in lines:
			if str(chat_id) == row['chat_id']:
				user_id = int(row['user_id'])
				row['crop_type'] = crop_type
				row['harvested'] = 'False'
				break
	f.close()

	# Write back
	with open('user_list.csv', 'w') as f:
		w = csv.DictWriter(f, fieldnames = r.fieldnames)
		w.writeheader()
		w.writerows(lines)
	f.close()

	if crop_type == '':
		bot.sendMessage(chat_id, 'Successfully deleted')
	else:
		bot.sendMessage(chat_id, 'Successfully registered')



# clear data
def clear(chat_id):
	pass
#	bot.sendMessage(chat_id, 'Delete photos and videos...')
#	subprocess.call('rm data/*', shell=True)
#	with open('data.txt', 'w') as f:
#		f.write('-1')
#	bot.sendMessage(chat_id, 'Done')



def message_default(msg, content_type, chat_type, chat_id):

	global last_command

# Inline Keyboard
	menu_main = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text='My Crops', callback_data='crop')],
		[InlineKeyboardButton(text='Exchange', callback_data='exchange')],
		[InlineKeyboardButton(text='My Info', callback_data='info')],
	])

# Read command
	if content_type == 'text':
		arguments = msg['text'].strip().lower().split()
		if arguments[0] == '/photo':
			photo(chat_id)

		elif arguments[0] == '/video':
			video(chat_id)

		elif arguments[0] == '/status':
			status(chat_id)

		elif arguments[0] == '/lighten':
			leaf_command(chat_id, b"L")

		elif arguments[0] == '/dim':
			leaf_command(chat_id, b"D")

		elif arguments[0] == '/water':
			leaf_command(chat_id, b"w")

		elif arguments[0] == '/harvest':
			harvest(chat_id)

		elif arguments[0] == '/ex':
			if len(arguments) > 1:
				ex(chat_id,arguments[1])
			else:
				bot.sendMessage(chat_id, 'Please enter the type of the crop')
				last_command[chat_id] = Command.ex

		elif arguments[0] == '/request':
			if len(arguments) > 1:
				request(chat_id,arguments[1])
			else:
				bot.sendMessage(chat_id, 'Please enter the user ID')
				last_command[chat_id] = Command.request

		elif arguments[0] == '/register':
			if len(arguments) > 1:
				register(chat_id,arguments[1])
			else:
				bot.sendMessage(chat_id, 'Please enter the type of the crop')
				last_command[chat_id] = Command.register_existing

		elif arguments[0] == '/del':
			register(chat_id,'')

		elif msg['text'].strip().lower() == 'chu chu yeah':
			bot.sendMessage(chat_id, 'Please me')
			last_command[chat_id] = Command.chuchuyeah

		else:
			bot.sendMessage(chat_id, 'What would you like to do?', reply_markup=menu_main)

	else:
		bot.sendMessage(chat_id, 'What would you like to do?', reply_markup=menu_main)



def message_chuchuyeah(msg, content_type, chat_type, chat_id):

	global last_command

	if content_type == 'text':
		arguments = msg['text'].strip().lower().split()

		if msg['text'].strip().lower() == 'chu chu yeah':
			bot.sendMessage(chat_id, 'Without you')
	
		else :
			message_default(msg, content_type, chat_type, chat_id)
	else :
		message_default(msg, content_type, chat_type, chat_id)

	last_command[chat_id] = Command.none



def message_ex(msg, content_type, chat_type, chat_id):

	global last_command

	if content_type == 'text':
		crop_type = msg['text'].strip().lower()
		going_to_request = ex(chat_id,crop_type)
		if going_to_request == True:
			last_command[chat_id] = Command.request
		else:
			last_command[chat_id] = Command.none
		
	else :
		message_default(msg, content_type, chat_type, chat_id)
		last_command[chat_id] = Command.none



def message_request(msg, content_type, chat_type, chat_id):

	global last_command

	if content_type == 'text':
		user_id = msg['text'].strip().lower()
		request(chat_id,user_id)
		
	else :
		message_default(msg, content_type, chat_type, chat_id)

	last_command[chat_id] = Command.none



def message_register_existing(msg, content_type, chat_type, chat_id):

	global last_command

	if content_type == 'text':
		crop_type = msg['text'].strip().lower()
		register(chat_id,crop_type)
		
	else :
		message_default(msg, content_type, chat_type, chat_id)

	last_command[chat_id] = Command.none



Command = Enum('Command',
              'none chuchuyeah ex request register_existing')

options = {Command.none : message_default,
           Command.chuchuyeah : message_chuchuyeah,
           Command.ex : message_ex,
           Command.request : message_request,
           Command.register_existing : message_register_existing}

last_command = {}

def on_chat_message(msg):
	content_type, chat_type, chat_id = telepot.glance(msg)

	if chat_id not in last_command:
		last_command[chat_id] = Command.none

#	print(content_type, chat_type, chat_id)
	options[last_command[chat_id]](msg, content_type, chat_type, chat_id)
	#message_default(msg, content_type, chat_type, chat_id)



def on_callback_query(msg):
	query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
#	print('Callback Query:', query_id, from_id, query_data) # -> Callback Query: 637684716986582353 148472543 press

	# define 
	menu_crop = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text='Get Photo', callback_data='photo')],
		[InlineKeyboardButton(text='Get Video', callback_data='video')],
		[InlineKeyboardButton(text='Get Status', callback_data='status')],
		[InlineKeyboardButton(text='Lighten', callback_data='lighten')],
		[InlineKeyboardButton(text='Dim', callback_data='dim')],
		[InlineKeyboardButton(text='Harvest', callback_data='harvest')],
	])

	menu_exchange = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text='Available Crops', callback_data='available')],
		[InlineKeyboardButton(text='Exchange Crops', callback_data='ex')],
	])

	menu_info = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text='Register Crop', callback_data='register')],
		[InlineKeyboardButton(text='Delete Crop', callback_data='del')],
		# [InlineKeyboardButton(text='Clear Photos and Videos', callback_data='clear')],
	])

#	bot.answerCallbackQuery(query_id, text='Got it') # Pop-up message

	# Main Menu
	if query_data == 'crop':
		bot.sendMessage(from_id, 'My Crops', reply_markup=menu_crop)
	elif query_data == 'exchange':
		bot.sendMessage(from_id, 'Exchange', reply_markup=menu_exchange)
	elif query_data == 'info':
		bot.sendMessage(from_id, 'My Info', reply_markup=menu_info)

	# My Crops
	elif query_data == 'photo':
		photo(from_id)
	elif query_data == 'video':
		video(from_id)
	elif query_data == 'status':
		status(from_id)
	elif query_data == 'lighten':
		leaf_command(from_id, b"L")
	elif query_data == 'dim':
		leaf_command(from_id, b"D")
	elif query_data == 'harvest':
		harvest(from_id)

	# Exchange
	elif query_data == 'available':
		available(from_id)
	elif query_data == 'ex':
		bot.sendMessage(from_id, 'Please enter the type of the crop')
		last_command[from_id] = Command.ex

	# My Info
	elif query_data == 'register':
		bot.sendMessage(from_id, 'Please enter the type of the crop')
		last_command[from_id] = Command.register_existing
	elif query_data == 'del':
		register(from_id,'')
	elif query_data == 'clear':
		clear(from_id)

	# Request Response
	elif query_data.split()[0] == 'accept':
		bot.sendMessage(from_id, 'Request Accepted')
		bot.sendMessage(query_data.split()[1], 'Request for '+ query_data.split()[2] + ' from ' + query_data.split()[3] + ' has been accepted')
	elif query_data.split()[0] == 'deny':
		bot.sendMessage(from_id, 'Request Denied')
		bot.sendMessage(query_data.split()[1], 'Request for '+ query_data.split()[2] + ' from ' + query_data.split()[3] + ' has been denied')

# Main program

PWD = os.getcwd()
bot = telepot.Bot('321380226:AAF6x7YH4uk5fpCtMVdcAKgnd0x_0zWaps4')

bot.message_loop({'chat': on_chat_message, 'callback_query': on_callback_query})
print ('Listening ...')

# Keep the program running.
while 1:
	time.sleep(10)

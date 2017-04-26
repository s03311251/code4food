#!/usr/bin/python3
import time
import telepot
import subprocess
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

chuchuyeah = False

def photo(chat_id):

	with open('data.txt', 'r') as f:
		photo_id = int(f.readline())

	if photo_id == -1:
		bot.sendMessage(chat_id, 'Error: No photo found')

	else:
		bot.sendMessage(chat_id, 'Sending photo...')
		photo_name = "data/" + str(photo_id).zfill(10) + ".jpg" # photo name is 10-digit long

		print('Opening ',photo_name)

		with open(photo_name, 'rb') as f:
			bot.sendPhoto(chat_id, f)



def video(chat_id):

	# get the correct photo_id
	with open('data.txt', 'r') as f:
		photo_id_end = int(f.readline())

	if photo_id_end == -1:
		bot.sendMessage(chat_id, 'Error: No photo found')
		
	else:
		bot.sendMessage(chat_id, 'Making video...')

		photo_id_start = photo_id_end - 120 # make last 120 photos into video
		if ( photo_id_start < 0):
			photo_id_start = 0

		# call ffmpeg to make video
		command = 'ffmpeg -y -framerate 10 -start_number '+ str(photo_id_start) +' -i data/%10d.jpg -c:v libtheora -r 10 data/output.ogg' # photo name is 10-digit long
		subprocess.call(command, shell=True)

		bot.sendMessage(chat_id, 'Sending video...')

		# send video
		with open('data/output.ogg', 'rb') as f:
			bot.sendVideo(chat_id, f)



# clear data
def clear(chat_id):
	bot.sendMessage(chat_id, 'Delete photos and videos...')
	subprocess.call('rm data/*', shell=True)
	with open('data.txt', 'w') as f:
		f.write('-1')
	bot.sendMessage(chat_id, 'Done')



def on_chat_message(msg):
	content_type, chat_type, chat_id = telepot.glance(msg)
#	print(content_type, chat_type, chat_id)

# Inline Keyboard
	menu_main = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text='My Crops', callback_data='crop')],
		[InlineKeyboardButton(text='Exchange', callback_data='exchange')],
		[InlineKeyboardButton(text='My Info', callback_data='info')],
	])

	menu_crop = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text='Get Photo', callback_data='photo')],
		[InlineKeyboardButton(text='Get Video', callback_data='video')],
		[InlineKeyboardButton(text='Lighten', callback_data='lighten')],
		[InlineKeyboardButton(text='Dim', callback_data='dim')],
	])	

# Read command
	if content_type == 'text':
		if msg['text'].strip().lower() == '/photo':
			photo(chat_id)
		elif msg['text'].strip().lower() == '/video':
			video(chat_id)
		elif msg['text'].strip().lower() == '/clear':
			clear(chat_id)
		elif msg['text'].strip().lower() == 'chu chu yeah':
			global chuchuyeah
			if chuchuyeah == False:
				bot.sendMessage(chat_id, 'Please me')
				chuchuyeah = True
			else:
				bot.sendMessage(chat_id, 'Without you')
				chuchuyeah = False
		else:
			bot.sendMessage(chat_id, 'What would you like to do?', reply_markup=menu_crop)
	else:
		bot.sendMessage(chat_id, 'What would you like to do?', reply_markup=menu_crop)



def on_callback_query(msg):
	query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
#	print('Callback Query:', query_id, from_id, query_data) # -> Callback Query: 637684716986582353 148472543 press

	# define 
	menu_crop = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text='Get Photo', callback_data='photo')],
		[InlineKeyboardButton(text='Get Video', callback_data='video')],
		[InlineKeyboardButton(text='Lighten', callback_data='lighten')],
		[InlineKeyboardButton(text='Dim', callback_data='dim')],
		[InlineKeyboardButton(text='Harvest', callback_data='harvest')],
	])

	menu_exchange = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text='Available Crops', callback_data='available')],
		[InlineKeyboardButton(text='I\'m Feeling Lucky', callback_data='lucky')],
	])

	menu_info = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text='Reset Password', callback_data='pw')],
		[InlineKeyboardButton(text='Clear Photos and Videos', callback_data='clear')],
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
	if query_data == 'lighten':
		pass
	if query_data == 'dim':
		pass
	if query_data == 'harvest':
		pass

	# Exchange
	if query_data == 'available':
		pass
	if query_data == 'lucky':
		pass

	# My Info
	if query_data == 'pw':
		pass
	if query_data == 'clear':
		clear(from_id)


# Main program

bot = telepot.Bot('321380226:AAF6x7YH4uk5fpCtMVdcAKgnd0x_0zWaps4')

bot.message_loop({'chat': on_chat_message, 'callback_query': on_callback_query})
print ('Listening ...')

# Keep the program running.
while 1:
	time.sleep(10)






# # Send message
#		bot.sendMessage(148472543, 'Hey!')

# # Analysis message
# 		chat_id = msg['chat']['id']
# 		print(chat_id)

#		print (bot.getMe())
# -> {'first_name': 'code4food', 'username': 'code4food_bot', 'id': 321380226}

#		response = bot.getUpdates(offset=624391780)
# offset=(sth) avoid old messages
#		print(response)

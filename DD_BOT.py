import config
import sqlite3
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup as InMa, InlineKeyboardButton as InBu
import random
from datetime import datetime

# Внутренние костыли
regular = []
dictionary = {}

# Подключаем бота
bot = Bot(config.TOKEN)
dp = Dispatcher(bot)

# Подключаемся к бд
db = sqlite3.connect('server.db')
sql = db.cursor()

#Клавиатура
Button_plus = InBu("+", callback_data = "+")
Button_minus = InBu("-", callback_data = "-")

Keyboard = InMa().row(Button_plus, Button_minus)

# БД
sql.execute("""CREATE TABLE IF NOT EXISTS users (
		MessageText TEXT,
		BotAnswer INT,
		UserAnswer TEXT,
		TimeMessage TEXT,
		Author TEXT
	)""")

# Ещё один внутренний костыль
array_index = []

# Захват сообщений
@dp.message_handler()
async def on_message(message: types.message):
	# Проверка на наличие пользователя в списке
	for i in array_index:
		regular.extend(i)
	if message.from_user.username not in regular:
		# Регистрация пользователя
		array_index.append([message.from_user.username])
		dictionary[message.from_user.username] = array_index.index([message.from_user.username])
		print(array_index, "User logged in, bot is running ")
		await bot.send_message(message.from_user.id, "Введите вопрос")
	else:
		# Проверка на то, вводит ли человек вопрос или ответ
		if message.text != "-" and message.text != "+":
			try:
			# Замена значений разделов в таблице	
				array_index[dictionary[message.from_user.username]][1] = message.text
				bot_response = await bot.send_message(message.from_user.id, str(random.randint(0,1)))
				dictionary[message.chat.id] = (await bot.send_message(message.from_user.id,"Ответ верный(+) или нет(-)",reply_markup=Keyboard)).message_id ####
				array_index[dictionary[message.from_user.username]][2] = bot_response.text
			# Создание разделов в таблице 	
			except IndexError: 
				array_index[dictionary[message.from_user.username]].append(message.text) 
				bot_response = await bot.send_message(message.from_user.id, str(random.randint(0,1)))
				dictionary[message.chat.id] = (await bot.send_message(message.from_user.id,"Ответ верный(+) или нет(-)",reply_markup=Keyboard)).message_id ####
				array_index[dictionary[message.from_user.username]].append(bot_response.text)

		else:
			# Проверка на наличие вопроса
			if len(array_index[dictionary[message.from_user.username]]) > 1:
					# Замена значения раздела
				try:
					array_index[dictionary[message.from_user.username]][3] = str(datetime.now())[0:19]
					array_index[dictionary[message.from_user.username]][4] = message.text
					# Создание раздела под ответ 
				except:
					array_index[dictionary[message.from_user.username]].append(str(datetime.now())[0:19])
					array_index[dictionary[message.from_user.username]].append(message.text)
				# Внесение данных в бд	
				sql.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (array_index[dictionary[message.from_user.username]][1], array_index[dictionary[message.from_user.username]][2], array_index[dictionary[message.from_user.username]][4], array_index[dictionary[message.from_user.username]][3], array_index[dictionary[message.from_user.username]][0] ))
				db.commit()
				print(array_index)
				await bot.delete_message(message.from_user.id, dictionary[message.from_user.id])
				await bot.send_message(message.from_user.id, "Вопрос зарегестрирован, введите следующий:")
			else:
				# Ответ на (ответ без заданного вопроса)(Багоюз)
				print("багоюзер ", message.from_user.username)
				await bot.send_message(message.from_user.id, "Сначала вопрос")
				
# Отлов callback_data с клавиатуры 
@dp.callback_query_handler(text="+")
async def cb(query:types.CallbackQuery):
	try:
		array_index[dictionary[query.from_user.username]][3] = str(datetime.now())[0:19]
		array_index[dictionary[query.from_user.username]][4] = "+"
	# Создание раздела под ответ 
	except:
		array_index[dictionary[query.from_user.username]].append(str(datetime.now())[0:19])
		array_index[dictionary[query.from_user.username]].append("+")
		# Внесение данных в бд	
	sql.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (array_index[dictionary[query.from_user.username]][1], array_index[dictionary[query.from_user.username]][2], array_index[dictionary[query.from_user.username]][4], array_index[dictionary[query.from_user.username]][3], array_index[dictionary[query.from_user.username]][0] ))
	db.commit()
	#print(array_index)
	await bot.delete_message(query.from_user.id, dictionary[query.from_user.id])
	print(array_index)
	await bot.send_message(query.from_user.id, "Вопрос зарегестрирован, введите следующий:")

@dp.callback_query_handler(text="-")
async def cb(query:types.CallbackQuery):
	try:
		array_index[dictionary[query.from_user.username]][3] = str(datetime.now())[0:19]
		array_index[dictionary[query.from_user.username]][4] = "-"
	# Создание раздела под ответ 
	except:
		array_index[dictionary[query.from_user.username]].append(str(datetime.now())[0:19])
		array_index[dictionary[query.from_user.username]].append("-")
		# Внесение данных в бд	
	sql.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (array_index[dictionary[query.from_user.username]][1], array_index[dictionary[query.from_user.username]][2], array_index[dictionary[query.from_user.username]][4], array_index[dictionary[query.from_user.username]][3], array_index[dictionary[query.from_user.username]][0] ))
	db.commit()
	#print(array_index)
	await bot.delete_message(query.from_user.id, dictionary[query.from_user.id])
	print(array_index)
	await bot.send_message(query.from_user.id, "Вопрос зарегестрирован, введите следующий:")

if __name__ == '__main__':
	executor.start_polling(dp, skip_updates=True)
import telebot
import json
from func import load_data, save_data
from game_func import get_game_data

with open("config.json", encoding='utf-8') as f:
    token = json.load(f)

TOKEN = token['token']
abouts = token['abouts']

# считывание данных при запуске
data = load_data()

bot = telebot.TeleBot(token=TOKEN)

# все команды бота
bot.set_my_commands([
    telebot.types.BotCommand('start', 'Начать'),
    telebot.types.BotCommand('help', 'Помощь'),
    telebot.types.BotCommand('about', 'Расскажу о себе'),
    telebot.types.BotCommand('hopla', 'Начать квест'),
])


# спиисок команд для команды help
commands = {
    '/start': 'Начать общение с ботом',
    '/help': 'Показать эту команды',
    '/about': 'Расскажу о себе',
    '/hopla': 'Определить какой ты хлеб'
}

# возвращает глобальную переменную
def global_data():
    global data
    return data

#считывание уровня
def get_level(user_id):
    data = global_data()
    return data[user_id]["level"]

# вывод клавиатуры
def keyboard_handler(message, level):
    game_data = get_game_data()
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    for key, value in game_data[level]['options'].items():
        button = telebot.types.InlineKeyboardButton(text=key, callback_data=value)
        keyboard.add(button)
    bot.send_message(message.chat.id, game_data[level]['description'], reply_markup=keyboard)

# проверяет есть ли пользователь. Сбрасывает данные
def user_check(message):
    data = global_data()
    user_id = str(message.chat.id)
    if user_id not in data.keys():
        data[user_id] = {
            "name": message.from_user.first_name,
            "level": "start",
            "result": "",
            "toggle": 0
        }
    return data

# возвращает id пользователя
def get_id(message):
    return message.chat.id

# обработки команды start
@bot.message_handler(commands=['start'])
def start_message(message):
    data = global_data()
    bot.send_message(message.chat.id,'Привет')
    data = load_data()
    bot.send_message(message.chat.id, "Напиши /help для помощи!")


# обработка команды help
@bot.message_handler(commands=['help'])
def help_message(message):
    text = "Вот список команд, которые я могу выполнить:\n"
    for command, description in commands.items():
        text += f'{command} - {description}\n'
    bot.send_message(message.chat.id, text)


# обработка команды about
@bot.message_handler(commands=['about'])
def about_message(message):
    bot.send_message(message.chat.id, abouts)

# обработка нажатий на клавиатуре
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    # удаление кнопок на прошлом сообщении
    bot.edit_message_reply_markup(call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
    data = global_data()
    user_id = str(get_id(call.message))
    # ставим 1 чтобы команда hopla не работала, пока активны остальные кнопки
    data[user_id]["toggle"] = 1
    game_data = get_game_data()
    level = call.data
    with open(game_data[level]["path"], "rb") as f:
        bot.send_photo(call.message.chat.id, f)
    if level in game_data["game_result"]["win"]:
        bot.send_message(call.message.chat.id, game_data[level]["description"])
        bot.send_message(call.message.chat.id, "Вы выиграли!")
        data[user_id]['result'] = "Выиграл"
        data[user_id]['level'] = "start"
        data[user_id]["toggle"] = 0
        save_data(data)
    elif level in game_data["game_result"]["lose"]:
        bot.send_message(call.message.chat.id, game_data[level]["description"])
        bot.send_message(call.message.chat.id, "Вы проиграли!")
        data[user_id]['result'] = "Проиграл"
        data[user_id]['level'] = "start"
        data[user_id]["toggle"] = 0
        save_data(data)
    else:
        if level == "back":
            bot.send_message(call.message.chat.id, game_data[level]["description"])
            level = "start"
            with open(game_data[level]["path"], "rb") as f:
                bot.send_photo(call.message.chat.id, f)
        data[user_id]['level'] = level
        save_data(data)
        keyboard_handler(call.message, level)


# основная функция для игры
@bot.message_handler(commands=['hopla'])
def hopla_handler(message):
    data = global_data()
    data = user_check(message)
    user_id = str(get_id(message))
    c = data[user_id]['toggle']
    # выводим только если прошлое сообщение не hopla и нет активных кнопок
    if c == 0:
        data[user_id]["toggle"] = 1
        game_data = get_game_data()
        level = get_level(user_id)
        with open(game_data[level]["path"], "rb") as f:
            bot.send_photo(message.chat.id, f)
        if level in game_data["game_result"]["win"]:
            bot.send_message(message.chat.id, game_data[level]["description"])
            bot.send_message(message.chat.id, "Вы выиграли!")
            data[user_id]['result'] = "Выиграл"
            data[user_id]['level'] = "start"
            save_data(data)
        elif level in game_data["game_result"]["lose"]:
            bot.send_message(message.chat.id, game_data[level]["description"])
            bot.send_message(message.chat.id, "Вы проиграли!")
            data[user_id]['result'] = "Проигал"
            data[user_id]['level'] = "start"
            save_data(data)
        else:
            data[user_id]['level'] = level
            save_data(data)
            keyboard_handler(message, level)


# обработка текстовых запросов
@bot.message_handler(content_types=['text'])
def text_func(message):
    if "привет" in message.text.lower():
        bot.send_message(message.chat.id, "Привет!")
    if "как дела" in message.text.lower():
        bot.send_message(message.chat.id, "Все круто! А у т ебя?\n")
        bot.send_message(message.chat.id, "Как дела?")
    if "что" and "делаешь" in message.text.lower():
        bot.send_message(message.chat.id, "С тобой общаюсь!")
    if not "привет" in message.text.lower() and not "как дела" in message.text.lower() and not ("что" and "делаешь" in message.text.lower()):
        bot.send_message(message.chat.id, "Я тебя не понял!")


bot.polling()
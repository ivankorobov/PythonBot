import telebot
from telebot import types

headers = {"X-RapidAPI-Key": "b91096a6abmshdd935d9258b2b62p114503jsn98c819f45f9f",
           "X-RapidAPI-Host": "hotels4.p.rapidapi.com"}

bot = telebot.TeleBot('5716175138:AAGV8B6e4HDe0cyzvyWre4CcET1v5Bi5Qlk')


def get_menu(message):

    """ Функция создает в телеграм боте функциональные кнопки меню """

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    button_lowprice = types.KeyboardButton(text='/lowprice')
    button_highprice = types.KeyboardButton(text='/highprice')
    button_bestdeal = types.KeyboardButton(text='/bestdeal')
    button_history = types.KeyboardButton(text='/history')
    button_help = types.KeyboardButton(text='/help')
    markup.add(button_lowprice, button_highprice, button_bestdeal, button_history, button_help)
    bot.send_message(message.chat.id, text='<b>Главное меню</b>.\nВыберете команду:', reply_markup=markup, parse_mode='html')


@bot.message_handler(commands=['start'])
def command_start(message):

    """ Функция бля запуска команды /start """

    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}')
    get_menu(message)


@bot.message_handler(commands=['help'])
def command_help(message):

    """ Функция для запуска команды /help """

    help_message = f'<i>Топ самых <b><u>дешёвых</u></b> отелей в городе \n(команда <b>/lowprice</b>).</i>\n\n'\
                   '<i>Топ самых <b><u>дорогих</u></b> отелей в городе \n(команда <b>/highprice</b>).</i>\n\n'\
                   '<i>Топ отелей, <b><u>наиболее подходящих по цене и расположению от центра</u></b> \n\t(команда '\
                   '<b>/bestdeal)</b>.</i>\n\n'\
                   '<i>Историю поиска отелей \n(команда <b>/history)</b>.</i>\n\n'

    bot.send_message(message.chat.id, help_message, parse_mode='html')


@bot.message_handler(commands=['lowprice'])
def command_lowprice(message):

    """ Функция для запуска команды /lowprice """

    bot.send_message(message.chat.id, text='/lowprice команда!')



@bot.message_handler(commands=['highprice'])
def command_help(message):

    """ Функция для запуска команды /highprice """

    bot.send_message(message.chat.id, text='/highprice команда!')



@bot.message_handler(commands=['bestdeal'])
def command_help(message):

    """ Функция для запуска команды /bestdeal """

    bot.send_message(message.chat.id, text='/bestdeal команда!')



@bot.message_handler(commands=['history'])
def command_help(message):

    """ Функция для запуска команды /history """

    bot.send_message(message.chat.id, text='/history команда!')



@bot.message_handler(content_types=['text'])
def handler_text(message):

    """ Функция для обработки сообщений и команд, которые не знает бот """

    bot.send_message(message.chat.id, text='Неизвестная команда!')


bot.polling(none_stop=True)

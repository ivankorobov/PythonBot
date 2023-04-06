from loader import bot
from telebot import types


def get_menu(message):
    """ Функция создает в телеграм боте функциональные кнопки меню """

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    button_lowprice = types.KeyboardButton(text='/lowprice')
    button_highprice = types.KeyboardButton(text='/highprice')
    button_bestdeal = types.KeyboardButton(text='/bestdeal')
    button_history = types.KeyboardButton(text='/history')
    button_help = types.KeyboardButton(text='/help')
    markup.add(button_lowprice, button_highprice, button_bestdeal, button_history, button_help)
    bot.send_message(message.chat.id, text='<b>Главное меню</b>.\nВыберете команду:',
                     reply_markup=markup,
                     parse_mode='html')


def find_end(message):
    """ Функция создает кнопки меню  после успешного выполнения выбраной команды """

    get_menu(message)

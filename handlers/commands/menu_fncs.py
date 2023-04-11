from telebot import types
from loader import bot
from handlers.default_handlers.start import get_menu


def key_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(types.KeyboardButton('Главное меню'))
    bot.send_message(message.chat.id, text='Введите название города', reply_markup=markup)


def back_key(markup):
    markup.add(types.KeyboardButton('Назад'))
    markup.add(types.KeyboardButton('Главное меню'))


def find_end(message):
    get_menu(message)

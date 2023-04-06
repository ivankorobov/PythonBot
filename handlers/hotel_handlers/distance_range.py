from telebot import types
from loader import bot
from handlers.side_functions import get_menu, back_key
from handlers.api import get_city
from handlers.hotel_handlers import check_from_to, get_price_from


def get_distance_from(message):
    """ Функция для установления значения от какого радиуса необходимо провести поиск отеля """

    if message.text == 'Назад':
        bot.send_message(message.chat.id, text='Введите название города:', reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_city)
    elif message.text == 'Главное меню':
        get_menu(message)
    elif check_from_to(message=message, func_name=get_distance_from.__name__):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        back_key(markup)
        bot.send_message(message.chat.id, text=f'Искать в радиусе до (miles):',
                         reply_markup=markup)
        bot.register_next_step_handler(message, get_distance_to)
    else:
        bot.register_next_step_handler(message, get_distance_from)


def get_distance_to(message):
    """ Функция для установления значения до какого радиуса необходимо провести поиск отеля """

    if message.text == 'Назад':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        back_key(markup)
        bot.send_message(message.chat.id, text=f'Искать в радиусе от (miles):',
                         reply_markup=markup)
        bot.register_next_step_handler(message, get_distance_from)
    elif message.text == 'Главное меню':
        get_menu(message)
    elif check_from_to(message=message, func_name=get_distance_to.__name__):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        back_key(markup)
        bot.send_message(message.chat.id, text=f'Искать в стоимости за ночь от (USD):',
                         reply_markup=markup)
        bot.register_next_step_handler(message, get_price_from)
    else:
        bot.register_next_step_handler(message, get_distance_to)

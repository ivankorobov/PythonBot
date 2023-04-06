from telebot import types
from loader import bot
from handlers.side_functions import get_menu, back_key
from handlers.hotel_handlers import get_distance_to, check_from_to, check_in


def get_price_from(message):
    """ Функция для установления значения минимальной стоимости ночи в отеле поиск отеля """

    if message.text == 'Назад':
        bot.send_message(message.chat.id, text=f'Искать в радиусе до (miles):')
        bot.register_next_step_handler(message, get_distance_to)
    elif message.text == 'Главное меню':
        get_menu(message)
    elif check_from_to(message=message, func_name=get_price_from.__name__):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        back_key(markup)
        bot.send_message(message.chat.id, text=f'Искать в стоимости за ночь до (USD):',
                         reply_markup=markup)
        bot.register_next_step_handler(message, get_price_to)

    else:
        bot.register_next_step_handler(message, get_price_from)


def get_price_to(message):
    """ Функция для установления значения максимальной стоимости ночи в отеле поиск отеля"""

    if message.text == 'Назад':
        bot.send_message(message.chat.id, text=f'Искать в стоимости за ночь от (USD):',
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_price_from)
    elif message.text == 'Главное меню':
        get_menu(message)
    elif check_from_to(message=message, func_name=get_price_to.__name__):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        back_key(markup)
        bot.send_message(message.chat.id, text=f'Выберете дату выезда:', reply_markup=markup)
        check_in(message)
    else:
        bot.register_next_step_handler(message, get_price_to)

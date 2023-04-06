from telebot import types
from loader import bot
from main import result_find
from handlers.side_functions import get_menu, back_key
from handlers.hotel_handlers import get_count_hotel
from handlers.api import get_result


def get_photo(message):
    """ Функция спрашивает сколько отелей отобразить вместе с отелем """

    if message.text.lower() == 'да':
        result_find['Flag_Photos'] = True

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True). \
            add(*(types.KeyboardButton(str(i_num)) for i_num in range(1, 6)), row_width=3)
        back_key(markup)
        bot.send_message(message.from_user.id, text='Сколько фото показать(не более 5)?', reply_markup=markup)
        bot.register_next_step_handler(message, get_count_photo)
    elif message.text.lower() == 'нет':
        result_find['Flag_Photos'] = False
        get_result(message)
    elif message.text == 'Назад':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True). \
            add(*(types.KeyboardButton(str(i_num)) for i_num in range(1, 11)), row_width=5)
        back_key(markup)
        bot.send_message(message.chat.id, text='Сколько отелей показать(не более 10)?', reply_markup=markup)
        bot.register_next_step_handler(message, get_count_hotel)
    elif message.text == 'Главное меню':
        get_menu(message)
    else:
        bot.send_message(message.chat.id, text='<b>Ошибка!!</b>\nНе верная команда!', parse_mode='html')
        bot.register_next_step_handler(message, get_count_hotel)


def get_count_photo(message):
    """ Функция спрашивает необходимо ли отобразить фото в результате поиска"""

    if message.text.isdigit() and int(message.text) > 0:
        count_photo = int(message.text)
        if count_photo >= 5:
            count_photo = 5

        result_find['Count_photo'] = int(count_photo)
        get_result(message)

    elif message.text == 'Главное меню':
        get_menu(message)

    elif message.text == 'Назад':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        key_yes = types.KeyboardButton(text='Да')
        key_no = types.KeyboardButton(text='Нет')
        keyboard.add(key_yes, key_no)
        bot.send_message(message.chat.id, text='Результат поиска показать с фото?', reply_markup=keyboard)
        bot.register_next_step_handler(message, get_photo)
    else:
        bot.send_message(message.chat.id, '<b>Ошибка!!</b>\nВведите корректное число фотографий(не более 5):',
                         parse_mode='html')
        bot.register_next_step_handler(message, get_count_photo)

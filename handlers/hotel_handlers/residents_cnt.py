from telebot import types
from loader import bot
from main import result_find
from handlers.side_functions import get_menu, back_key
from handlers.hotel_handlers import get_count_hotel, check_out


def get_resident(message):
    """ Функция для получения значения жильцов в номере отеля """

    if message.text.isdigit() and 9 > int(message.text) > 0:
        result_find['Adults'] = int(message.text)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True).\
            add(*(types.KeyboardButton(str(i_num)) for i_num in range(1, 11)), row_width=5)
        back_key(markup)
        bot.send_message(message.chat.id, text='Сколько отелей показать(не более 10)?', reply_markup=markup)
        bot.register_next_step_handler(message, get_count_hotel)
    elif message.text == 'Назад':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        back_key(markup)
        bot.send_message(message.chat.id, text='Дата выезда(day.month.year):', reply_markup=markup)
        bot.register_next_step_handler(message, check_out)
    elif message.text == 'Главное меню':
        get_menu(message)
    else:
        bot.send_message(message.chat.id, f'<b>Ошибка!!</b>\nВведите корректное число жильцов:', parse_mode='html')
        bot.register_next_step_handler(message, get_resident)

from telebot import types
from loader import bot
from main import result_find
from handlers.side_functions import get_menu
from handlers.api import get_city
from date_range import check_in
from distance_range import get_distance_from


def get_id_and_city(message, locations_and_id):

    locations_and_id = list(locations_and_id)

    if message.text in [''.join(i_city) for i_city in [list(locale) for locale in locations_and_id]]:
        result_find['Country'] = message.text
        for i_dict in locations_and_id:
            if i_dict.get(message.text) is not None:
                result_find['regionId'] = str(i_dict.get(message.text))
                break

        if result_find['SortOrder_distance'] is True:
            bot.send_message(message.chat.id, text=f'Искать в радиусе от (miles):',
                             reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(message, get_distance_from)
        elif result_find['SortOrder_distance'] is False:
            bot.send_message(message.chat.id, text='Выберете дату заезда:', reply_markup=types.ReplyKeyboardRemove())
            check_in(message)
        else:
            bot.send_message(message.chat.id, text='<b>Ошибка!!</b>', parse_mode='html')
            get_menu(message)
    elif message.text == 'Назад':
        bot.send_message(message.chat.id, 'Введите название города.', reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_city)
    elif message.text == 'Главное меню':
        get_menu(message)
    else:
        bot.send_message(message.chat.id, text='<b>Ошибка!!</b>\nВыберете город из списка!', parse_mode='html')
        bot.register_next_step_handler(message, get_id_and_city, locations_and_id)

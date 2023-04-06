from telebot import types
import requests
import config
from loader import bot
from handlers.side_functions import get_menu, write_json, back_key
from handlers.hotel_handlers import get_id_and_city


def get_city(message):
    """ Функция проверяет наличие ключа/сообщения из чата в библиотеке locations/search """

    if message.text == 'Главное меню':
        get_menu(message)
    else:
        url_loc = "https://hotels4.p.rapidapi.com/locations/v3/search"

        querystring = {"q": message.text, "locale": 'ru_RU', "langid": "1033", "siteid": "300000001"}
        print(querystring)
        response_loc = requests.request("GET", url_loc, headers=config.headers, params=querystring)
        print(response_loc, '- response_loc')
        date_locations = write_json(response_loc)

        try:
            if 'gaiaId' in date_locations["sr"][0]:
                locations_and_id = [{date_city['regionNames']['fullName']: date_city['gaiaId']}
                                    for date_city in date_locations["sr"]
                                    if 'gaiaId' in date_city]
                print(locations_and_id, '- locations_and_id')
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
                for i_dict in locations_and_id:
                    for i_key in i_dict.keys():
                        markup.add(types.KeyboardButton(i_key))
                back_key(markup)
                bot.send_message(message.chat.id, 'Выберете город из списка.', reply_markup=markup)
                bot.register_next_step_handler(message, get_id_and_city, locations_and_id)

            else:
                bot.send_message(message.chat.id, '<b>Санкции!!</b>\n'
                                                  'Введите название города расположенного вне территории РФ:',
                                 parse_mode='html')
                bot.register_next_step_handler(message, get_city)

        except AttributeError:
            bot.send_message(message.chat.id, '<b>Ошибка!!</b>\n'
                                              'Введите название города еще раз:',
                             parse_mode='html')
            bot.register_next_step_handler(message, get_city)

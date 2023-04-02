import telebot
from telebot import types
from telegram_bot_calendar import DetailedTelegramCalendar
from datetime import datetime
from datetime import date, timedelta
import config
import json
import requests
import re

bot = telebot.TeleBot(config.TOKEN)

history_list = list()
result_find = dict()
my_step_time = {'y': 'год', 'm': 'месяц', 'd': 'день'}


def write_json(date_j):

    """ Функция создания json объекта """

    date_j = json.loads(date_j.text)
    return date_j


def get_city(message):

    """ Функция проверяет наличие ключа/сообщения из чата в библиотеке locations/search """

    result_find['language'] = result_find.get('language', ['en_US', 'M'])
    result_find['currency'] = result_find.get('currency', ['USD', '$'])

    url_loc = "https://hotels4.p.rapidapi.com/locations/v2/search"

    querystring_loc = {"query": message.text, "locale": result_find['language'][0],
                             "currency": result_find['currency'][0]}
    response_loc = requests.request("GET", url_loc, headers=config.headers, params=querystring_loc)
    date_locations = write_json(response_loc)
    try:
        if date_locations.get("moresuggestions") > 0:
            locations_and_id = [{''.join(re.sub(r"</span>", '', ''.join(re.sub(r"<span class='\w+'>", '',
                                                                     date_city["caption"])))):
                                           date_city["destinationId"]} for date_city in
                                      date_locations["suggestions"][0]["entities"]]

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            for i_dict in locations_and_id:
                for i_key in i_dict.keys():
                    markup.add(types.KeyboardButton(i_key))

            bot.send_message(message.chat.id, 'Выберете город из списка.', reply_markup=markup)
            bot.register_next_step_handler(message, get_id_and_city, locations_and_id)

        else:
            bot.send_message(message.chat.id, '<b>Ошибка!!</b>\nВведите название города.', parse_mode='html')
            bot.register_next_step_handler(message, get_city)
    except AttributeError:
        bot.send_message(message.chat.id, '<b>Ошибка!!</b>\nВведите название города еще раз:',
                         parse_mode='html')
        bot.register_next_step_handler(message, get_city)


def get_id_and_city(message, locations_and_id):

    locations_and_id = list(locations_and_id)

    if message.text in [''.join(i_city) for i_city in [list(locale) for locale in locations_and_id]]:
        result_find['Country'] = message.text
        for i_dict in locations_and_id:
            if i_dict.get(message.text) is not None:
                result_find['DestinationId'] = int(i_dict.get(message.text))
                break

        if result_find['SortOrder_distance'] is False:
            bot.send_message(message.chat.id, text='Выберете дату заезда:', reply_markup=types.ReplyKeyboardRemove())
            checkIn(message)
        else:
            bot.send_message(message.chat.id, text='<b>Ошибка!!</b>', parse_mode='html')
            get_menu(message)
    else:
        bot.send_message(message.chat.id, text='<b>Ошибка!!</b>\nВыберете город из списка!', parse_mode='html')
        bot.register_next_step_handler(message, get_id_and_city, locations_and_id)


def checkIn(message):

    """ Функция для получения даты заезда в отель из телеграмм чата """

    calendar, step = DetailedTelegramCalendar(calendar_id=1, min_date=date.today(), locale='ru').build()
    bot.send_message(message.chat.id, f"Выберете {my_step_time[step]}", reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def cal(call):
    result, key, step = DetailedTelegramCalendar(min_date=date.today(), locale='ru', calendar_id=1).process(call.data)

    if not result and key:
        bot.edit_message_text(f"Выберете {my_step_time[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Дата заезда: {result}.",
                              call.message.chat.id,
                              call.message.message_id)
        bot.send_message(call.message.chat.id, text='Выберете дату выезда:')
        result_find['CheckIn'] = result
        checkOut(call.message)


def checkOut(message):

    """ Функция для получения даты выезда из отеля из телеграмм чата """

    calendar, step = DetailedTelegramCalendar(
        calendar_id=2, min_date=result_find.get('CheckIn')+timedelta(days=1), locale='ru').build()
    bot.send_message(message.chat.id, f"Выберете {my_step_time[step]}", reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def cal(call):
    result, key, step = DetailedTelegramCalendar(min_date=result_find['CheckIn']+timedelta(days=1),
                                                 locale='ru', calendar_id=2).process(call.data)
    if not result and key:
        bot.edit_message_text(f"Выберете {my_step_time[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Дата выезда: {result}.",
                              call.message.chat.id,
                              call.message.message_id)
        result_find['CheckOut'] = result
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True). \
            add(*(types.KeyboardButton(str(i_num)) for i_num in range(1, 9)), row_width=4)
        bot.send_message(call.message.chat.id, text='Сколько человек будет проживать(!> 8):', reply_markup=markup)
        bot.register_next_step_handler(call.message, get_resident)


def get_resident(message):

    """ Функция для получения значения жильцов в номере отеля """

    if message.text.isdigit() and 9 > int(message.text) > 0:
        result_find['Adults1'] = int(message.text)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True).\
            add(*(types.KeyboardButton(str(i_num)) for i_num in range(1, 11)), row_width=5)
        bot.send_message(message.chat.id, text='Сколько отелей показать(!> 10)?', reply_markup=markup)
        bot.register_next_step_handler(message, get_count_hotel)
    else:
        bot.send_message(message.chat.id, f'<b>Ошибка!!</b>\nВведите корректное число жильцов:', parse_mode='html')
        bot.register_next_step_handler(message, get_resident)

def get_count_hotel(message):

    """ Функция для получения числа отображаемых в чате отелей """

    if message.text.isdigit() and int(message.text) > 0:
        count_hotel: int = int(message.text)
        if count_hotel >= 10:
            count_hotel: int = 10
        if result_find['SortOrder_distance'] is True:
            result_find['Count_hotel_for'] = count_hotel
            count_hotel = 100
        result_find['PageSize'] = int(count_hotel)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        key_yes = types.KeyboardButton(text='Да')
        key_no = types.KeyboardButton(text='Нет')
        markup.add(key_yes, key_no)

        bot.send_message(message.chat.id, text='Результат поиска показать с фото?', reply_markup=markup)
        bot.register_next_step_handler(message, get_result)          #get_photo
    else:
        bot.send_message(message.chat.id, '<b>Ошибка!!</b>\nВведите корректное число отелей(Max 10):',
                         parse_mode='html')
        bot.register_next_step_handler(message, get_count_hotel)


# def get_photo(message):
#
#     """ Функция, которая спрашивает сколько отелей отобразить в результате поиска """
#
#     if message.text.lower() == 'да':
#
#         result_find['Flag_Photos'] = True
#         markup = types.ReplyKeyboardMarkup(resize_keyboard=True). \
#             add(*(types.KeyboardButton(str(i_num)) for i_num in range(1, 11)), row_width=5)
#
#         bot.send_message(message.from_user.id, text='Сколько фото показать(max 10)?', reply_markup=markup)
#         bot.register_next_step_handler(message, get_count_photo)
#     elif message.text.lower() == 'нет':
#         result_find['Flag_Photos'] = False
#         get_result(message)
#     else:
#         bot.send_message(message.chat.id, text='<b>Ошибка!!</b>\nНе верная команда!', parse_mode='html')
#         bot.register_next_step_handler(message, get_count_hotel)


# def get_count_photo(message):
#
#     """ Функция, которая спрашивает необходимо ли отобразить фото в результате поиска"""
#
#     if message.text.isdigit() and int(message.text) > 0:
#         count_photo = int(message.text)
#         if count_photo >= 10:
#             count_photo = 10
#
#         result_find['Count_photo'] = int(count_photo)
#         get_result(message)
#     else:
#         bot.send_message(message.chat.id, '<b>Ошибка!!</b>\nВведите корректное число фотографий(не более 10):',
#                          parse_mode='html')
#         bot.register_next_step_handler(message, get_count_photo)


def get_result(message):

    """ Функция, которая выводит результат поиска в чаб бота (ПОКА БЕЗ ФОТО)"""

    print(result_find, '- result_find')
    bot.send_message(message.chat.id, text=f'<u>Подождите, идет загрузка...</u>',
                     reply_markup=types.ReplyKeyboardRemove(), parse_mode='html')
    url_price = "https://hotels4.p.rapidapi.com/properties/list"
    querystring_price = {"destinationId": result_find['DestinationId'], "pageNumber": "1",
                               "pageSize": result_find['PageSize'], "checkIn": str(result_find['CheckIn']),
                               "checkOut": str(result_find['CheckOut']), "adults1": result_find['Adults1'],
                               "sortOrder": result_find['SortOrder'],
                               "locale": result_find['language'][0],
                               "currency": result_find['currency'][0]}
    print(querystring_price, '- querystring_price')
    response_price = requests.request("GET", url_price, headers=config.headers, params=querystring_price)
    print(response_price, '- response_price')
    date_price = write_json(response_price)
    date_price = date_price["data"]["body"]["searchResults"]["results"]

    for i_hotel in date_price:
        message_str = 'Отель: {hotel_name}\n' \
                      'Адрес: {hotel_address}\n' \
                      'Рейтинг {hotel_rating}\n' \
                      'Удаленность от центра {hotel_distance}\n' \
                      'Цена за ночь {price}\n' \
                      'Цена за все время: {all_price}\n' \
                      'Сайт: {website}'.format(
                        hotel_name=i_hotel.get("name"),
                        hotel_address=f'{i_hotel["address"]["locality"]}, '
                                      f'{i_hotel["address"].get("streetAddress")}',
                        hotel_rating=i_hotel.get("guestReviews", '-')["unformattedRating"],
                        hotel_distance=i_hotel["landmarks"][0].get("distance"),
                        price=str(result_find.get('currency')[1]) + str(int(''.join(re.findall(r'\d\S+',
                        i_hotel["ratePlan"]["price"]["current"])).replace(',', ''))),
                        all_price=str(result_find.get('currency')[1]) +
                        str(int(''.join(re.findall(r'\d\S+', i_hotel["ratePlan"]["price"]["current"])).
                                replace(',', '')) * result_find.get("Adults1")
                        * int((result_find.get("CheckOut") - result_find.get("CheckIn")).days)),
                        website='https://www.hotels.com/ho' + str(i_hotel["id"]))

        bot.send_message(message.chat.id, message_str)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton('ОК'))
    bot.send_message(message.chat.id, text=f'<b>Поиск завершен</b>', parse_mode='html', reply_markup=markup)


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

    result_find['SortOrder'] = 'PRICE'

    result_find['SortOrder_distance'] = False

    result_find['Command'] = message.text
    bot.send_message(message.chat.id, text='Введите название города')

    bot.register_next_step_handler(message, get_city)



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


if __name__ == '__main__':

    bot.polling(none_stop=True)

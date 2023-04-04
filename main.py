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


def key_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(types.KeyboardButton('Главное меню'))
    bot.send_message(message.chat.id, text='Введите название города', reply_markup=markup)


def back_key(markup):
    markup.add(types.KeyboardButton('Назад'))
    markup.add(types.KeyboardButton('Главное меню'))

def write_json(date_j):

    """ Функция создания json объекта """

    date_j = json.loads(date_j.text)
    return date_j


def get_city(message):

    """ Функция проверяет наличие ключа/сообщения из чата в библиотеке locations/search """

    if message.text == 'Главное меню':
        get_menu(message)
    else:
        url_loc = "https://hotels4.p.rapidapi.com/locations/v3/search"

        querystring = {"q": message.text, "locale": 'ru_RU', "langid": "1033", "siteid": "300000001"}

        response_loc = requests.request("GET", url_loc, headers=config.headers, params=querystring)
        date_locations = write_json(response_loc)
        try:
            if date_locations.get("rc") == "OK":
                locations_and_id = [{date_city['regionNames']['fullName']: date_city['gaiaId']} for date_city in
                                          date_locations["sr"] if 'gaiaId' in date_city]
                print(locations_and_id, '- locations_and_id')
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
                for i_dict in locations_and_id:
                    for i_key in i_dict.keys():
                        markup.add(types.KeyboardButton(i_key))
                back_key(markup)
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
                result_find['regionId'] = str(i_dict.get(message.text))
                break

        if result_find['SortOrder_distance'] is False:
            bot.send_message(message.chat.id, text='Выберете дату заезда:', reply_markup=types.ReplyKeyboardRemove())
            checkIn(message)
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
        back_key(markup)
        bot.send_message(call.message.chat.id, text='Сколько человек будет проживать(!> 8):', reply_markup=markup)
        bot.register_next_step_handler(call.message, get_resident)


def get_resident(message):

    """ Функция для получения значения жильцов в номере отеля """

    if message.text.isdigit() and 9 > int(message.text) > 0:
        result_find['Adults'] = int(message.text)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True).\
            add(*(types.KeyboardButton(str(i_num)) for i_num in range(1, 11)), row_width=5)
        back_key(markup)
        bot.send_message(message.chat.id, text='Сколько отелей показать(!> 10)?', reply_markup=markup)
        bot.register_next_step_handler(message, get_count_hotel)
    elif message.text == 'Назад':
        markup: telebot = types.ReplyKeyboardMarkup(resize_keyboard=True)
        back_key(markup)
        bot.send_message(message.chat.id, text='Дата выезда(day.month.year):', reply_markup=markup)
        bot.register_next_step_handler(message, checkOut)
    elif message.text == 'Главное меню':
        get_menu(message)
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
        back_key(markup)
        bot.send_message(message.chat.id, text='Результат поиска показать с фото?', reply_markup=markup)
        bot.register_next_step_handler(message, get_photo)

    elif message.text == 'Назад':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True). \
            add(*(types.KeyboardButton(str(i_num)) for i_num in range(1, 9)), row_width=4)
        back_key(markup)
        bot.send_message(message.chat.id, text='Сколько человек будет проживать(Max 8):', reply_markup=markup)
        bot.register_next_step_handler(message, get_resident)

    elif message.text == 'Главное меню':
        get_menu(message)

    else:
        bot.send_message(message.chat.id, '<b>Ошибка!!</b>\nВведите корректное число отелей(Max 10):',
                         parse_mode='html')
        bot.register_next_step_handler(message, get_count_hotel)


def get_address(id_num):

    """ Функция, которая получает адрес отеля"""

    url = "https://hotels4.p.rapidapi.com/properties/v2/detail"

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "propertyId": id_num
    }

    response = requests.request("POST", url, json=payload, headers=config.headers)
    address = write_json(response)
    return address['data']['propertyInfo']['summary']['location']['address']['addressLine']


def get_images(id_num):

    url = "https://hotels4.p.rapidapi.com/properties/v2/detail"

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "propertyId": id_num
    }

    response = requests.request("POST", url, json=payload, headers=config.headers)
    date_img = write_json(response)
    img_str = [types.InputMediaPhoto(
        date_img["data"]['propertyInfo']['propertyGallery']['images'][i_num]['image']['url'])
        for i_num in range(result_find['Count_photo'])]
    print(img_str)
    return img_str


def get_photo(message: telebot) -> None:

    """ Функция, которая спрашивает сколько отелей отобразить в результате поиска """

    if message.text.lower() == 'да':
        result_find['Flag_Photos'] = True

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True). \
            add(*(types.KeyboardButton(str(i_num)) for i_num in range(1, 11)), row_width=5)
        back_key(markup)
        bot.send_message(message.from_user.id, text='Сколько фото показать(max 5)?', reply_markup=markup)
        bot.register_next_step_handler(message, get_count_photo)
    elif message.text.lower() == 'нет':
        result_find['Flag_Photos'] = False
        get_result(message)
    elif message.text == 'Назад':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True). \
            add(*(types.KeyboardButton(str(i_num)) for i_num in range(1, 11)), row_width=5)
        back_key(markup)
        bot.send_message(message.chat.id, text='Сколько отелей показать(max 10)?', reply_markup=markup)
        bot.register_next_step_handler(message, get_count_hotel)
    elif message.text == 'Главное меню':
        get_menu(message)
    else:
        bot.send_message(message.chat.id, text='<b>Ошибка!!</b>\nНе верная команда!', parse_mode='html')
        bot.register_next_step_handler(message, get_count_hotel)


def get_count_photo(message: telebot) -> None:

    """ Функция, которая спрашивает необходимо ли отобразить фото в результате поиска"""

    if message.text.isdigit() and int(message.text) > 0:
        count_photo = int(message.text)
        if count_photo >= 5:
            count_photo = 5

        result_find['Count_photo'] = int(count_photo)
        get_result(message)

    elif message.text == 'Главное меню':
        get_menu(message)

    elif message.text == 'Назад':
        keyboard: telebot = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        key_yes: telebot = types.KeyboardButton(text='Да')
        key_no: telebot = types.KeyboardButton(text='Нет')
        keyboard.add(key_yes, key_no)
        bot.send_message(message.chat.id, text='Результат поиска показать с фото?', reply_markup=keyboard)
        bot.register_next_step_handler(message, get_photo)
    else:
        bot.send_message(message.chat.id, '<b>Ошибка!!</b>\nВведите корректное число фотографий(не более 5):',
                         parse_mode='html')
        bot.register_next_step_handler(message, get_count_photo)



def get_result(message):

    """ Функция, которая выводит результат поиска в чаб бота (ПОКА БЕЗ ФОТО)"""

    print(result_find, '- result_find')
    bot.send_message(message.chat.id, text=f'<u>Подождите, идет загрузка...</u>',
                     reply_markup=types.ReplyKeyboardRemove(), parse_mode='html')
    url_price = "https://hotels4.p.rapidapi.com/properties/v2/list"
    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "destination": {"regionId": result_find['regionId']},
        "checkInDate": {
            "day": result_find['CheckIn'].day,
            "month": result_find['CheckIn'].month,
            "year": result_find['CheckIn'].year
        },
        "checkOutDate": {
            "day": result_find['CheckOut'].day,
            "month": result_find['CheckOut'].month,
            "year": result_find['CheckOut'].year
        },
        "rooms": [{"adults": result_find['Adults']}],
        "resultsStartingIndex": 0,
        "resultsSize": result_find['PageSize'],
        "sort": result_find['SortOrder'],
        "filters": {"price": {
            "max": 99999,
            "min": 1
        }}
    }
    print(payload, '- payload')

    response = requests.request("POST", url_price, json=payload, headers=config.headers)
    print(response, '- response_price')

    date_price = write_json(response)
    date_price = date_price["data"]["propertySearch"]["properties"]

    for i_hotel in date_price:
        address = get_address(i_hotel["id"])
        message_str = '<b>Отель</b>: {hotel_name}\n' \
                      '<b>Адрес</b>: {hotel_address}\n' \
                      '<b>Рейтинг</b>: {hotel_rating}\\10 ★ \n' \
                      '<b>Удаленность от центра</b>: {hotel_distance} miles\n' \
                      '<b>Цена за ночь</b>: ${price}\n' \
                      '<b>Цена за все время</b>: ${all_price}\n' \
                      '<b>Сайт</b>: {website}'.format(
                        hotel_name=i_hotel["name"],
                        hotel_address=address,
                        hotel_rating=i_hotel["reviews"]['score'],
                        hotel_distance=i_hotel["destinationInfo"]['distanceFromDestination']['value'],
                        price=round(i_hotel['price']['lead']['amount']),
                        all_price=round(i_hotel['price']['lead']['amount'] *
                                        result_find['Adults'] *
                                        (int((result_find["CheckOut"] - result_find["CheckIn"]).days))),
                        website='https://www.hotels.com')

        if result_find['Flag_Photos']:
            media = get_images(i_hotel["id"])
            bot.send_message(message.chat.id, message_str, parse_mode='html')
            bot.send_media_group(message.chat.id, media)
        elif not result_find['Flag_Photos']:
            bot.send_message(message.chat.id, message_str, parse_mode='html')
        else:
            bot.send_message(message.chat.id, 'Произошла ошибка')

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

    result_find['SortOrder'] = "PRICE_LOW_TO_HIGH"

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

import time
import telebot
from telebot import types
from telegram_bot_calendar import DetailedTelegramCalendar
from datetime import datetime
from datetime import date, timedelta
from loader import bot
from api_requests.api_req import result_req, get_address, get_images, get_locations_and_id
from handlers.default_handlers.start import get_menu
from handlers.commands.menu_fncs import back_key, find_end
from handlers.commands.bestdeal_chk import get_distance_from
from main import result_find, history_list, my_step_time


def get_city(message):
    """ Функция проверяет наличие ключа/сообщения из чата в библиотеке locations/search """

    if message.text == 'Главное меню':
        get_menu(message)
    else:
        date_locations = get_locations_and_id(message)
        if 'gaiaId' in date_locations["sr"][0]:
            locations_and_id = [{date_city['regionNames']['fullName']: date_city['gaiaId']}
                                for date_city in date_locations["sr"]
                                if 'gaiaId' in date_city]
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
            result_find['Wait'] = True
            bot.register_next_step_handler(message, get_distance_from)
            while result_find['Wait']:
                time.sleep(1)
            else:
                check_in(message)
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


def check_in(message):
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
        check_out(call.message)


def check_out(message):
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
        bot.send_message(call.message.chat.id, text='Сколько человек будет проживать(не более 8):', reply_markup=markup)
        bot.register_next_step_handler(call.message, get_resident)


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
        markup: telebot = types.ReplyKeyboardMarkup(resize_keyboard=True)
        back_key(markup)
        bot.send_message(message.chat.id, text='Дата выезда(day.month.year):', reply_markup=markup)
        bot.register_next_step_handler(message, check_out)
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
        bot.send_message(message.chat.id, text='Сколько человек будет проживать(не более 8):', reply_markup=markup)
        bot.register_next_step_handler(message, get_resident)
    elif message.text == 'Главное меню':
        get_menu(message)
    else:
        bot.send_message(message.chat.id, '<b>Ошибка!!</b>\nВведите корректное число отелей(Max 10):',
                         parse_mode='html')
        bot.register_next_step_handler(message, get_count_hotel)


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


def get_result(message):
    """ Функция, которая выводит результат поиска в чаб бота """

    bot.send_message(message.chat.id, text=f'<u>Подождите, идет загрузка...</u>',
                     reply_markup=types.ReplyKeyboardRemove(), parse_mode='html')

    date_price = result_req()

    if date_price["data"]:
        date_price = date_price["data"]["propertySearch"]["properties"]
        if result_find['SortOrder_distance'] is True:
            date_price = list(filter(lambda i_hotel_best:
                                     result_find['distance_from'] <
                                     i_hotel_best["destinationInfo"]['distanceFromDestination']['value'] <
                                     result_find['distance_to'], date_price))

        if result_find['Command'] == '/highprice':
            date_price = list(filter(lambda i_hotel_best:
                                     0 < i_hotel_best['price']['lead']['amount'], date_price))
            date_price = sorted(date_price, key=lambda elem: (elem['price']['lead']['amount']), reverse=True)

        command_str = result_find['Command']
        date_command: datetime.date = datetime.now().replace(microsecond=0).strftime("%H:%M:%S %d.%m.%Y")
        hotel_str = [i_hotel["name"] for i_hotel in date_price[:result_find['PageSize']]]
        history_list.append({'Command': command_str, 'Date_time': date_command, 'Hotel_list': hotel_str})

        for i_hotel in date_price[:result_find['PageSize']]:
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
                            website=f'https://www.hotels.com/h{i_hotel["id"]}.Hotel-Information')

            if result_find['Flag_Photos']:
                media = get_images(i_hotel["id"])
                bot.send_message(message.chat.id, message_str, parse_mode='html')
                bot.send_media_group(message.chat.id, media)
            elif not result_find['Flag_Photos']:
                bot.send_message(message.chat.id, message_str, parse_mode='html')
            else:
                bot.send_message(message.chat.id, 'Произошла ошибка')

        if len(date_price) == 0:
            bot.send_message(message.chat.id, text=f'<b>По вашим критериям не нашлось ни одного подходящего отеля</b>',
                             parse_mode='html')
        elif len(date_price) < result_find['PageSize']:
            bot.send_message(message.chat.id, text=f'<b>Это все предложения, которые нам удалось найти для вас</b>',
                             parse_mode='html')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton('ОК'))
        bot.send_message(message.chat.id, text=f'<b>Поиск завершен</b>', parse_mode='html', reply_markup=markup)
        bot.register_next_step_handler(message, find_end)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton('ОК'))
        bot.send_message(message.chat.id, text=f'<b>По вашим критериям не нашлось ни одного подходящего отеля\n'
                                               f'Попробуйте задать другие параметры поиска</b>',
                         parse_mode='html', reply_markup=markup)
        bot.register_next_step_handler(message, find_end)


from telebot import types
import requests
from datetime import datetime
import config
from loader import bot
from main import result_find, history_list
from handlers.side_functions import write_json, find_end
from handlers.api import get_images, get_address


def get_result(message):
    """ Функция, которая выводит результат поиска в чаб бота """

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
        "filters": {
            "star": result_find['StarsCount']
        }
    }

    if result_find['SortOrder_distance'] is True:
        payload["filters"]["price"] = {"max": result_find['price_to'], "min": result_find['price_from']}
        del payload["resultsSize"]
    print(payload, '- payload')

    response = requests.request("POST", url_price, json=payload, headers=config.headers)
    print(response, '- response_price')

    date_price = write_json(response)
    date_price = date_price["data"]["propertySearch"]["properties"]

    if result_find['SortOrder_distance'] is True:
        date_price = list(filter(lambda i_hotel_best:
                                 result_find['distance_from'] <
                                 i_hotel_best["destinationInfo"]['distanceFromDestination']['value'] <
                                 result_find['distance_to'], date_price))

    command_str = result_find['Command']
    date_command = datetime.now().replace(microsecond=0).strftime("%H:%M:%S %d.%m.%Y")
    hotel_str = [i_hotel["name"] for i_hotel in date_price[:result_find['PageSize']]]
    history_list.append({'Command': command_str, 'Date_time': date_command, 'Hotel_list': hotel_str})

    print(date_price, '- date_price')
    print(len(date_price), '- len(date_price)')
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

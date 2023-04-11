import json
import requests
from telebot import types
import config
from main import result_find


def get_locations_and_id(message):
    """ Функция проверяет наличие ключа/сообщения из чата в библиотеке locations/search """

    url_loc = "https://hotels4.p.rapidapi.com/locations/v3/search"

    querystring = {"q": message.text, "locale": 'ru_RU', "langid": "1033", "siteid": "300000001"}
    response_loc = requests.request("GET", url_loc, headers=config.headers, params=querystring)
    date_locations = json.loads(response_loc.text)

    return date_locations


def get_address(id_num):
    """ Функция для получения адрес отеля"""

    url = "https://hotels4.p.rapidapi.com/properties/v2/detail"
    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "propertyId": id_num
    }
    response = requests.request("POST", url, json=payload, headers=config.headers)
    address = json.loads(response.text)

    return address['data']['propertyInfo']['summary']['location']['address']['addressLine']


def get_images(id_num):
    """ Функция для получения фотографий отеля"""

    url = "https://hotels4.p.rapidapi.com/properties/v2/detail"
    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "propertyId": id_num
    }
    response = requests.request("POST", url, json=payload, headers=config.headers)
    date_img = json.loads(response.text)
    img_str = [types.InputMediaPhoto(
        date_img["data"]['propertyInfo']['propertyGallery']['images'][i_num]['image']['url'])
        for i_num in range(result_find['Count_photo'])]

    return img_str


def result_req():
    """ Функция, которая выводит результат поиска в чаб бота """

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

    if result_find['Command'] == '/highprice':
        payload["resultsSize"] = 200
    if result_find['SortOrder_distance'] is True:
        payload["filters"]["price"] = {"max": result_find['price_to'], "min": result_find['price_from']}
        del payload["resultsSize"]
    response = requests.request("POST", url_price, json=payload, headers=config.headers)
    date_price = json.loads(response.text)

    return date_price

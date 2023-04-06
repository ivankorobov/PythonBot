from telebot import types
import requests
import config
from main import result_find
from handlers.side_functions import write_json


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
    address = write_json(response)
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
    date_img = write_json(response)
    img_str = [types.InputMediaPhoto(
        date_img["data"]['propertyInfo']['propertyGallery']['images'][i_num]['image']['url'])
        for i_num in range(result_find['Count_photo'])]
    print(img_str)
    return img_str

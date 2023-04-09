import json


def write_json(date_j):
    """ Функция создания json объекта из полученного словаря """

    date_j = json.loads(date_j.text)
    return date_j

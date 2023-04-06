from loader import bot
from main import result_find
from handlers.api import get_city


@bot.message_handler(commands=['lowprice'])
def command_lowprice(message):
    """ Функция для запуска команды /lowprice """

    result_find['SortOrder'] = "PRICE_LOW_TO_HIGH"
    result_find['StarsCount'] = ["10", "20", "30", "40", "50"]
    result_find['SortOrder_distance'] = False
    result_find['Command'] = message.text

    bot.send_message(message.chat.id, text='Введите название города')
    bot.register_next_step_handler(message, get_city)

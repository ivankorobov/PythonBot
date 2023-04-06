from loader import bot
from main import result_find
from handlers.api import get_city


@bot.message_handler(commands=['bestdeal'])
def command_bestdeal(message):
    """ Функция для запуска команды /bestdeal """

    result_find['SortOrder'] = "DISTANCE"
    result_find['StarsCount'] = ["10", "20", "30", "40", "50"]
    result_find['SortOrder_distance'] = True
    result_find['Command'] = message.text

    bot.send_message(message.chat.id, text='Введите название города')
    bot.register_next_step_handler(message, get_city)

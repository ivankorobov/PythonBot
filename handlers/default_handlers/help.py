from loader import bot


@bot.message_handler(commands=['help'])
def command_help(message):

    """ Функция справка (команда /help) """

    help_message = f'<i>Список команд</i>' \
                   f'\n' \
                   f'<i>Топ самых <b><u>дешёвых</u></b> отелей в городе \n(команда <b>/lowprice</b>).</i>\n\n'\
                   '<i>Топ самых <b><u>дорогих</u></b> отелей в городе \n(команда <b>/highprice</b>).</i>\n\n'\
                   '<i>Топ отелей, <b><u>наиболее подходящих по цене и расположению от центра</u></b> \n\t(команда '\
                   '<b>/bestdeal)</b>.</i>\n\n'\
                   '<i>Историю поиска отелей \n(команда <b>/history)</b>.</i>\n\n'

    bot.send_message(message.chat.id, help_message, parse_mode='html')

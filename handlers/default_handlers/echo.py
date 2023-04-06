from loader import bot


@bot.message_handler(content_types=['text'])
def handler_text(message):

    """ Функция для обработки сообщений и команд, которые не знает бот """

    bot.send_message(message.chat.id, text='Неизвестная команда!\n'
                                           'Введи /help, чтобы узнать больше!')

from loader import bot
from handlers.side_functions.menu import get_menu


@bot.message_handler(commands=['start', 'hello'])
def command_start(message) -> None:

    """ Функция-приветствие (команды /start и /hello-world) """

    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}')
    get_menu(message)

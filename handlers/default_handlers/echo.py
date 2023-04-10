from loader import bot
from telebot import types


@bot.message_handler(content_types=['text'])
def handler_text(message):
    """ Функция для обработки сообщений и команд, которые не знает бот """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    button_help = types.KeyboardButton(text='/help')
    markup.add(button_help)
    bot.send_message(message.chat.id, text='<b>Неизвестная команда!</b>\nДля отображения доступных команд нажмите ⬇️',
                     reply_markup=markup,
                     parse_mode='html')

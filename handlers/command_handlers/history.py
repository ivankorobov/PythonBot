from loader import bot
from main import history_list


@bot.message_handler(commands=['history'])
def command_history(message):
    """ Функция для запуска команды /history """

    bot.send_message(message.chat.id, text=f'<u>История поиска:</u>', parse_mode='html')
    history_str = ''
    for i_num, index_history in enumerate(history_list):
        history_str += f'#{i_num + 1}\n'\
                       f'Время и дата: {str(index_history.get("Date_time"))}\n'\
                       f'Команда: {index_history.get("Command")}\n'\
                       f'Список отелей: {str(index_history.get("Hotel_list"))}\n\n'
    if history_str == '':
        bot.send_message(message.chat.id, text='Вы ничего не искали.\nИстория поиска пуста.')
    else:
        bot.send_message(message.chat.id, text=history_str)

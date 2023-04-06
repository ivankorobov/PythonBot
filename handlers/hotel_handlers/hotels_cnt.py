from telebot import types
from loader import bot
from main import result_find
from handlers.side_functions import get_menu, back_key
from handlers.hotel_handlers import get_photo, get_resident


def get_count_hotel(message):
    """ Функция для получения числа отображаемых в чате отелей """

    if message.text.isdigit() and int(message.text) > 0:
        count_hotel: int = int(message.text)
        if count_hotel >= 10:
            count_hotel: int = 10
        result_find['PageSize'] = int(count_hotel)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        key_yes = types.KeyboardButton(text='Да')
        key_no = types.KeyboardButton(text='Нет')
        markup.add(key_yes, key_no)
        back_key(markup)
        bot.send_message(message.chat.id, text='Результат поиска показать с фото?', reply_markup=markup)
        bot.register_next_step_handler(message, get_photo)

    elif message.text == 'Назад':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True). \
            add(*(types.KeyboardButton(str(i_num)) for i_num in range(1, 9)), row_width=4)
        back_key(markup)
        bot.send_message(message.chat.id, text='Сколько человек будет проживать(не более 8):', reply_markup=markup)
        bot.register_next_step_handler(message, get_resident)

    elif message.text == 'Главное меню':
        get_menu(message)

    else:
        bot.send_message(message.chat.id, '<b>Ошибка!!</b>\nВведите корректное число отелей(Max 10):',
                         parse_mode='html')
        bot.register_next_step_handler(message, get_count_hotel)

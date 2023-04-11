import telebot
from telebot import types
from loader import bot
# from handlers.commands.common_chk import check_in
from handlers.commands.menu_fncs import back_key
from handlers.default_handlers.start import get_menu
from main import result_find


def check_from_to(message, func_name):
    """ Функция для поверки и заполнения фильтра команды /bestdeal """

    name_key_d = func_name[4:]
    if func_name.startswith('get_distance'):
        word_check = 'Радиус'
    else:
        word_check = 'Стоимость за ночь'

    if func_name.endswith('from'):
        from_flag = True
        from_to = 'от'
    else:
        from_flag = False
        from_to = 'до'

    try:
        message_convector = int(message.text)
        try:
            if message_convector >= 0:
                if from_flag is False and name_key_d.startswith('distance'):
                    if message_convector < result_find['distance_from']:
                        bot.send_message(message.chat.id,
                                         text=f'<b>Ошибка!!</b>\n{word_check} поиска "до" не может быть меньше '
                                              f'чем "от"\nВведите {word_check.lower()} {from_to} которого '
                                              f'искать еще раз', parse_mode='html')
                        raise IndexError
                elif from_flag is False and name_key_d.startswith('price'):
                    if message_convector < result_find['price_from']:
                        bot.send_message(message.chat.id,
                                         text=f'<b>Ошибка!!</b>\n{word_check} поиска "до" не может быть меньше '
                                              f'чем "от"\nВведите {word_check.lower()} {from_to} которого '
                                              f'искать еще раз', parse_mode='html')
                        raise IndexError
                result_find[name_key_d] = message_convector
                return True

            else:
                bot.send_message(message.chat.id,
                                 text=f'<b>Ошибка!!</b>\n{word_check} поиска не может быть меньше 0\nВведите '
                                      f'{word_check.lower()} {from_to} которого искать еще раз', parse_mode='html')
                raise IndexError
        except IndexError:
            return False

    except ValueError:
        bot.send_message(message.chat.id, text=f'<b>Ошибка!!</b>\n{word_check} поиска должен быть числом\n'
                                               f'Введите {word_check.lower()} {from_to} '
                                               f'которого искать еще раз:', parse_mode='html')
        return False


def get_distance_from(message):
    """ Функция для установления значения от какого радиуса необходимо провести поиск отеля """

    if message.text == 'Главное меню':
        get_menu(message)
    elif check_from_to(message=message, func_name=get_distance_from.__name__):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        back_key(markup)
        bot.send_message(message.chat.id, text=f'Искать в радиусе до (miles):', reply_markup=markup)
        bot.register_next_step_handler(message, get_distance_to)
    else:
        bot.register_next_step_handler(message, get_distance_from)


def get_distance_to(message):
    """ Функция для установления значения до какого радиуса необходимо провести поиск отеля """

    if message.text == 'Назад':
        markup: telebot = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        back_key(markup)
        bot.send_message(message.chat.id, text=f'Искать в радиусе от (miles):', reply_markup=markup)
        bot.register_next_step_handler(message, get_distance_from)
    elif message.text == 'Главное меню':
        get_menu(message)
    elif check_from_to(message=message, func_name=get_distance_to.__name__):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        back_key(markup)
        bot.send_message(message.chat.id, text=f'Искать в стоимости за ночь от (USD):', reply_markup=markup)
        bot.register_next_step_handler(message, get_price_from)
    else:
        bot.register_next_step_handler(message, get_distance_to)


def get_price_from(message):
    """ Функция для установления значения минимальной стоимости ночи в отеле поиск отеля """

    if message.text == 'Назад':
        bot.send_message(message.chat.id, text=f'Искать в радиусе до (miles):')
        bot.register_next_step_handler(message, get_distance_to)
    elif message.text == 'Главное меню':
        get_menu(message)
    elif check_from_to(message=message, func_name=get_price_from.__name__):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        back_key(markup)
        bot.send_message(message.chat.id, text=f'Искать в стоимости за ночь до (USD):',
                         reply_markup=markup)
        bot.register_next_step_handler(message, get_price_to)
    else:
        bot.register_next_step_handler(message, get_price_from)


def get_price_to(message):
    """ Функция для установления значения максимальной стоимости ночи в отеле поиск отеля"""

    if message.text == 'Назад':
        bot.send_message(message.chat.id, text=f'Искать в стоимости за ночь от (USD):',
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_price_from)
    elif message.text == 'Главное меню':
        get_menu(message)
    elif check_from_to(message=message, func_name=get_price_to.__name__):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        back_key(markup)
        bot.send_message(message.chat.id, text=f'Выберете дату выезда:', reply_markup=markup)
        result_find['Wait'] = False
    else:
        bot.register_next_step_handler(message, get_price_to)

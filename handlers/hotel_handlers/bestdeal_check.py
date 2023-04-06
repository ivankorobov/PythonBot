from loader import bot
from main import result_find


def check_from_to(message, func_name):
    """ Функция для поверки и заполнения фильтра команды /bestdeal """

    name_key_d = func_name[4:]
    print(name_key_d)
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

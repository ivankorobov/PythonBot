from telebot import types
from telegram_bot_calendar import DetailedTelegramCalendar
from datetime import date, timedelta
from loader import bot
from main import result_find, my_step_time
from handlers.side_functions import back_key
from handlers.hotel_handlers import get_resident


def check_in(message):
    """ Функция для получения даты заезда в отель из телеграмм чата """

    calendar, step = DetailedTelegramCalendar(calendar_id=1, min_date=date.today(), locale='ru').build()
    bot.send_message(message.chat.id, f"Выберете {my_step_time[step]}", reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def cal1(call):
    result, key, step = DetailedTelegramCalendar(min_date=date.today(), locale='ru', calendar_id=1).process(call.data)

    if not result and key:
        bot.edit_message_text(f"Выберете {my_step_time[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Дата заезда: {result}.",
                              call.message.chat.id,
                              call.message.message_id)
        bot.send_message(call.message.chat.id, text='Выберете дату выезда:')
        result_find['CheckIn'] = result
        check_out(call.message)


def check_out(message):
    """ Функция для получения даты выезда из отеля из телеграмм чата """

    calendar, step = DetailedTelegramCalendar(
        calendar_id=2, min_date=result_find.get('CheckIn')+timedelta(days=1), locale='ru').build()
    bot.send_message(message.chat.id, f"Выберете {my_step_time[step]}", reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def cal2(call):
    result, key, step = DetailedTelegramCalendar(min_date=result_find['CheckIn']+timedelta(days=1),
                                                 locale='ru', calendar_id=2).process(call.data)
    if not result and key:
        bot.edit_message_text(f"Выберете {my_step_time[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Дата выезда: {result}.",
                              call.message.chat.id,
                              call.message.message_id)
        result_find['CheckOut'] = result
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True). \
            add(*(types.KeyboardButton(str(i_num)) for i_num in range(1, 9)), row_width=4)
        back_key(markup)
        bot.send_message(call.message.chat.id, text='Сколько человек будет проживать(не более 8):', reply_markup=markup)
        bot.register_next_step_handler(call.message, get_resident)

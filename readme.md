# Too Easy Travel Bot

## Телеграм бот, с помощью которого можно быстро найти лучшие отели по всему миру.
### _@Ez_Travel_bot_
## Инструкция по эксплуатации телеграм-бота.

***

### Перечень файлов проекта и краткое описание.

***
### Файлы в корне проекта:
1. __config.py__ - хранит информацию о токене бота и ключ от API
2. __loader.py__ - инициализирует телеграмм-бота
3. __main.py__ - запускает бота
4. __readme.md__ - инструкция по эксплуатации телеграмм-бота
5. __Requirements.txt__ - содержит список используемых зависимостей необходимых для работы бота

### Пакеты в корне проекта:
* #### 📁 _api_requests_:
* __init.py__ - инициализирует пакет api_requests и его содержимое
* __api_req.py__ - содержит функции для обращения к API hotels.com
* #### 📁 _handlers_:
* __init.py__ - инициализирует пакет handlers и его содержимое
* * #### 📁 _commands_:
* * __init.py__ - инициализирует пакет commands и его содержимое
* * __bestdeal_chk.py__ - дополнительная последовательность функций для команды /bestdeal
* * __common_chk.py__ - последовательность функций для вывода вопросов ботом пользователю и формирования запроса к API
при выполнении команды команд /highprice и /lowprice
* * __menu_fncs.py__ - содержит функции создающие кнопки "Главное меню" и "Назад" в чате
* * #### 📁 _default_handlers_:
* * __init.py__ - инициализирует пакет default_handlers и его содержимое
* * __bestdeal.py__ - хендлер, реагирующий на команду /bestdeal в чате
* * __echo.py__ - хендлер, реагирующий на неизвестные команды в чате
* * __help.py__ - хендлер, реагирующий на команду /help в чате
* * __highprice.py__ - хендлер, реагирующий на команду /highprice в чате
* * __history.py__ - хендлер, реагирующий на команду /history в чате
* * __lowprice.py__ - хендлер, реагирующий на команду /lowprice в чате
* * __start.py__ - хендлер, реагирующий на команду /start в чате
* #### 📁 _prtscs - папка с скриншотами работы бота_
***
## Инструкция по установке

1. Скопировать репозиторий
2. Установить зависимости из Requirements.txt
3. Запустить файл main.py

## Зависимости
```requirements.txt
requests~=2.28.2
python-telegram-bot-calendar~=1.0.5
pyTelegramBotAPI~=4.10.0
```
***
### Команды бота:
Основная функция бота поиск отелей по запросу пользователя, однако в боте также представлен дополнительный функционал:
* /start - запуск бота
* /help — перечень всех команд бота,
* /lowprice — вывод самых дешёвых отелей в городе,
* /highprice — вывод самых дорогих отелей в городе,
* /bestdeal — вывод отелей, наиболее подходящих по цене и расположению от центра.
* /history — вывод истории поиска отелей

### Работа бота (для примера взята команда lowprice):

Старт бота

![Start](/prtscs/start.png)

Выбираем команду lowprice, прописываем город поиска и выбираем из предложенного списка

![City](/prtscs/city.png)

Выбираем дату заезда и выезда из отеля

![Date_1](/prtscs/date1.png)

Вводим количество человек в номере

![Count_hotels](/prtscs/date2PLUSresidents.png)

Выбираем количество отелей для показа

![Photo](/prtscs/hotelsCNT.png)

Далее выбираем вывод отелей с фото, или без

![Count_photo](/prtscs/photos.png)

Ждём пока идёт загрузка списка подходящих отелей

![Load_hotels](/prtscs/loading.png)

Получаем результат

![Show_hotels](/prtscs/result.png)

**Автор:** Иван Коробов
**Tg:** @korobok38
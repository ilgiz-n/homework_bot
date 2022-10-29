# Homework Телеграм-бот 

## Описание проекта:

Бот получает обновления от Yandex Practicum API и отправляет сообщения в Telegram со статусом проверки домашнего задания.

Функционал:
- запрос Yandex Practicum API (по-умолчанию раз в 10 мин)
- преобразование ответа в сообщение со статусом
- отправка сообщения в Telegram со статусом либо с информацией о возникшей ошибке
- логирование сообщений и служебной информации

## Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/ilgiz-n/homework_bot.git
```

Перейти в директорию с проектом:

```
cd homework_bot
```

Создать файл следующего названия

```
.env
```

Записать в него переменные окружения
```
PRACTICUM_TOKEN = токен_к_API_Практикум.Домашка
TELEGRAM_TOKEN = токен_Вашего_Telegtam_бота
TELEGRAM_CHAT_ID = Ваш_Telegram_ID
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Запустить исполнение кода

```
python homework.py
```

## Системные требования:
- Python 3.7.3
- python-telegram-bot 13.7
- pytest, python-dotenv, requests



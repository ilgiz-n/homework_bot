import logging
import os
import sys
import time
from http import HTTPStatus

import requests
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TOKENS = ('PRACTICUM_TOKEN', 'TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

streamHandler = logging.StreamHandler(stream=sys.stdout)
fileHandler = logging.FileHandler('homework.log')
handlers = [streamHandler, fileHandler]
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s]  %(message)s',
    handlers=handlers
)
logger = logging.getLogger(__name__)


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message
        )
    except Exception as error:
        logger.error(f'Cбой при отправке сообщения в телеграм: {error}')


def get_api_answer(current_timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса.
    В случае успешного запроса должна вернуть ответ API,
    преобразовав его из формата JSON к типам данных Python.
    """
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except Exception as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')
        raise Exception(f'Ошибка при запросе к основному API: {error}')
    if response.status_code != HTTPStatus.OK:
        status_code = response.status_code
        logging.error(f'ENDPOINT недоступен. Код состояния {status_code}')
        raise Exception(f'ENDPOINT недоступен. Код состояния {status_code}')
    try:
        return response.json()
    except ValueError:
        logger.error('Ошибка преобразования ответа API из формата JSON')
        raise ValueError('Ошибка преобразования ответа API из формата JSON')


def check_response(response):
    """Проверяет ответ API на корректность.
    В качестве параметра функция получает ответ API, приведенный к типам данных
    Python. Если ответ API соответствует ожиданиям, то функция должна вернуть
    список домашних работ (он может быть и пустым), доступный в ответе API по
    ключу 'homeworks'.
    """
    keys = ('homework_name', 'status')
    if type(response) is not dict:
        raise TypeError('Ответ API не является словарем')
    try:
        homeworks = response['homeworks']
    except KeyError:
        for key in keys:
            if key not in homeworks[0]:
                message = f'В ответе API oтсутствует ожидаемый ключ {key}'
                logger.error(message)
    except Exception as error:
        logger.error(f'Ошибка при запросе к основному API: {error}')
    if type(homeworks) is not list:
        raise TypeError('Homeworks приходят не в виде списка')
    return homeworks


def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе статус этой работы.
    В случае успеха, функция возвращает подготовленную для отправки
    в Telegram строку, содержащую один из вердиктов словаря.
    """
    homework_status = homework.get('status')
    homework_name = homework.get('homework_name')
    verdict = HOMEWORK_STATUSES.get(homework_status)
    if homework_status not in HOMEWORK_STATUSES:
        raise KeyError(f'Недокументированный статус работы:{homework_status}')
    return (f'Изменился статус проверки работы "{homework_name}". {verdict}')


def check_tokens():
    """Проверка доступности переменных окружения (токенов)."""
    response = True
    for TOKEN in TOKENS:
        if globals()[TOKEN] is None:
            exit_message = f'Отсутствует переменная окружения {TOKEN}'
            logger.critical(exit_message)
            response = False
    return response


def main():
    """Основная логика работы бота."""
    STATUS = ''
    ERROR_CACHE_MESSAGE = ''
    if not check_tokens():
        exit()
    bot = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            try:
                homework = homeworks[0]
            except IndexError:
                raise IndexError('Список домашних работ пуст')
            message = parse_status(homework)
            if message != STATUS:
                send_message(bot, message)
                STATUS = message
                logging.info(f'Бот отправил сообщение: {message}')
            logging.debug('Новый статус отсутствует')
            current_timestamp = response.get("current_date")
            time.sleep(RETRY_TIME)
        except Exception as error:
            logger.error(error)
            error_message = str(error)
            if error_message != ERROR_CACHE_MESSAGE:
                send_message(bot, error_message)
                ERROR_CACHE_MESSAGE = error_message
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()

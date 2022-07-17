import logging
import os
import sys
import time
from http import HTTPStatus
from typing import Any

import requests
from dotenv import load_dotenv
from telegram import Bot, Message

from exceptions import (APIRequestError, EndpointNotFoundError,
                        HomeworkKeyError, HomeworkNotListError,
                        JSONDecodingError, MessagingError,
                        ResponseNotDictError, UnknownStatusError)

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TOKENS = ('PRACTICUM_TOKEN', 'TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

MESSAGING_INFO = 'Бот отправил сообщение: "{}"'
MESSAGING_ERROR = 'Ошибка при отправке сообщения: {}'
API_REQUEST_ERROR = ('Ошибка при запросе к основному API: {error}'
                     'endpoint: {url}, headers: {headers}, params: {params}')
ENDPOINT_NOT_FOUND = ('ENDPOINT недоступен. Код состояния {status_code}, '
                      'endpoint: {url}, headers: {headers}, params: {params}')
JSON_DECODING_ERROR = 'Ошибка преобразования ответа API из формата JSON'
RESPONSE_NOT_DICT = 'Ответ API не является словарем'
HOMEWORKS_NOT_LIST = 'Homeworks приходят не в виде списка'
HOMEWORK_KEY_NOT_FOUND = 'В ответе API oтсутствует ожидаемый ключ {}'
UNKNOWN_STATUS = 'Недокументированный статус работы: {}'
HOMEWORK_UPDATE = ('Изменился статус проверки работы '
                   '"{homework_name}". {verdict}')
TOKEN_NOT_FOUND = 'Отсутствует переменная окружения {}'


streamHandler = logging.StreamHandler(stream=sys.stdout)
fileHandler = logging.FileHandler('homework.log')
handlers = [streamHandler, fileHandler]


def send_message(bot: Bot, message: str) -> Message:
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message
        )
        logging.info(MESSAGING_INFO.format(message))
    except MessagingError as error:
        print(MESSAGING_ERROR.format(error))


def get_api_answer(current_timestamp: int) -> dict:
    """Делает запрос к единственному эндпоинту API-сервиса.
    В случае успешного запроса должна вернуть ответ API,
    преобразовав его из формата JSON к типам данных Python.
    """
    timestamp = current_timestamp or int(time.time())
    parameters = dict(
        url=ENDPOINT,
        headers=HEADERS,
        params={'from_date': timestamp})
    try:
        response = requests.get(**parameters)
    except APIRequestError as error:
        print(API_REQUEST_ERROR.format(error=error, **parameters))
    if response.status_code != HTTPStatus.OK:
        status_code = response.status_code
        raise EndpointNotFoundError(ENDPOINT_NOT_FOUND.format(
            status_code=status_code, **parameters))
    try:
        return response.json()
    except JSONDecodingError:
        print(JSON_DECODING_ERROR)


def check_response(response: dict) -> list:
    """Проверяет ответ API на корректность.
    В качестве параметра функция получает ответ API, приведенный к типам данных
    Python. Если ответ API соответствует ожиданиям, то функция должна вернуть
    список домашних работ (он может быть и пустым), доступный в ответе API по
    ключу 'homeworks'.
    """
    keys = ('homework_name', 'status')
    if not isinstance(response, dict):
        raise ResponseNotDictError(RESPONSE_NOT_DICT)
        # raise TypeError(RESPONSE_NOT_DICT)
    try:
        homeworks = response['homeworks']
    except HomeworkKeyError:
        for key in keys:
            if key not in homeworks[0]:
                print(HOMEWORK_KEY_NOT_FOUND.format(key))
    if not isinstance(homeworks, list):
        raise HomeworkNotListError(HOMEWORKS_NOT_LIST)
    return homeworks


def parse_status(homework: dict) -> str:
    """Извлекает из информации о конкретной домашней работе статус этой работы.
    В случае успеха, функция возвращает подготовленную для отправки
    в Telegram строку, содержащую один из вердиктов словаря.
    """
    homework_status = homework.get('status')
    homework_name = homework.get('homework_name')
    verdict = VERDICTS.get(homework_status)
    if homework_status not in VERDICTS:
        raise UnknownStatusError(UNKNOWN_STATUS.format(homework_status))
    return HOMEWORK_UPDATE.format(homework_name=homework_name, verdict=verdict)


def check_tokens() -> bool:
    """Проверка доступности переменных окружения (токенов)."""
    response = True
    for TOKEN in TOKENS:
        if globals()[TOKEN] is None:
            exit_message = TOKEN_NOT_FOUND.format(TOKEN)
            logging.critical(exit_message)
            response = False
    return response


def main() -> Any:
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
            if len(homeworks) == 0:
                logging.debug('Список домашних работ пуст')
            else:
                homework = homeworks[0]
                message = parse_status(homework)
                if message != STATUS:
                    send_message(bot, message)
                    STATUS = message
            current_timestamp = response.get("current_date")
        except Exception as error:
            logging.exception(error)
            error_message = str(error)
            if error_message != ERROR_CACHE_MESSAGE:
                send_message(bot, error_message)
                ERROR_CACHE_MESSAGE = error_message
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s]  %(message)s',
        handlers=handlers
    )
    logger = logging.getLogger(__name__)
    main()

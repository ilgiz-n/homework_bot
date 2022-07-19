
# Исключения для бота


class MessagingError(Exception):
    """Ошибка отправки сообщения."""

    pass


class APIRequestError(Exception):
    """Ошибка доступа к API."""

    pass


class EndpointNotFoundError(Exception):
    """Ошибка доступа к ENDPOINT."""

    pass


class JSONDecodingError(Exception):
    """Ошибка преобразования ответа API из формата JSON."""

    pass


class ResponseNotDictError(TypeError):
    """Ответ API не является словарем."""

    pass


class HomeworkNotListError(TypeError):
    """Домашки представлены не в виде списка."""

    pass


class HomeworkKeyError(Exception):
    """Отсутствие ожидаемых ключей в ответе API."""

    pass


class UnknownStatusError(KeyError):
    """Недокументированном статусе домашней работы."""

    pass

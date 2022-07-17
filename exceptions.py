
# Исключения для бота


class MessagingError(Exception):
    """Вызывается при ошибке при отправки сообщения."""

    pass


class APIRequestError(Exception):
    """Вызывается при ошибке доступа к API."""

    pass


class EndpointNotFoundError(Exception):
    """Вызывается при ошибке доступа к ENDPOINT."""

    pass


class JSONDecodingError(Exception):
    """Вызывается при ошибке преобразовании ответа API из формата JSON."""

    pass


class ResponseNotDictError(Exception):
    """Вызывается, если ответ API не является словарем."""

    pass


class HomeworkNotListError(Exception):
    """Вызывается, если ответы представлены не в виде списка."""

    pass


class HomeworkKeyError(Exception):
    """Вызывается, при отсутствии ожидаемых ключей в ответе API."""

    pass


class UnknownStatusError(Exception):
    """Вызывается, при недокументированном статусе домашней работы."""

    pass

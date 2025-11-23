class NotAuthorizedError(Exception):
    """Ошибка авторизации"""

    pass


class CurrencyNotFoundError(Exception):
    """Ошибка поиска валюты"""

    pass


class InsufficientFundsError(Exception):
    """Ошибка недостаточных средств"""

    pass


class ApiRequestError(Exception):
    """Базовое исключение для ошибок API запросов"""

    def __init__(self, message: str, status_code: int | None = None, url: str | None = None):
        self.message = message
        self.status_code = status_code
        self.url = url
        super().__init__(self.message)


class ApiKeyError(ApiRequestError):
    """Ошибка API ключа"""

    pass


class RateLimitError(ApiRequestError):
    """Превышен лимит запросов"""

    pass


class NetworkError(ApiRequestError):
    """Сетевая ошибка"""

    pass

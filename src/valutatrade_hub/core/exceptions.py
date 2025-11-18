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
    """Ошибка запроса к API"""
    pass

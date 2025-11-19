import functools
from typing import Any, Callable, TypeVar

from src.valutatrade_hub.core.exceptions import (
    InsufficientFundsError,
    NotAuthorizedError,
)


def error_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RuntimeError as e:
            print(f"Системная ошибка: {e}")
        except NotAuthorizedError:
            print("Сначала выполните login")
        except InsufficientFundsError as e:
            print(f"Недостаточно средств: {e}")
        except FileNotFoundError as e:
            print(f"Файл не найден: {e}")
        except KeyError as e:
            print(f"Ключ не найден: {e}")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")

    return wrapper


T = TypeVar("T")


def check_auth(func: Callable[..., T]) -> Callable[..., T]:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        if not args or args[0] is None:
            raise NotAuthorizedError("Authentication required")
        return func(*args, **kwargs)

    return wrapper

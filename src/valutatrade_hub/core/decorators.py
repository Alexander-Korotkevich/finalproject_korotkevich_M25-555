import functools
from typing import Any, Callable, ParamSpec, TypeVar, cast
from src.valutatrade_hub.core.exceptions import NotAuthorizedError


def error_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RuntimeError as e:
            print(f"Системная ошибка: {e}")
        except NotAuthorizedError as e:
            print("Сначала выполните login")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")

    return wrapper


T = TypeVar("T")


def check_auth(func: Callable[..., T]) -> Callable[..., T]:
    def wrapper(*args: Any, **kwargs: Any) -> T:
        if not args or args[0] is None:
            raise NotAuthorizedError("Authentication required")
        return func(*args, **kwargs)

    return wrapper

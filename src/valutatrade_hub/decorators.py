from datetime import datetime
import functools
from typing import Any, Callable, TypeVar

from src.valutatrade_hub.core import utils
from src.valutatrade_hub.core.exceptions import (
    CurrencyNotFoundError,
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
        except CurrencyNotFoundError as e:
            print(e)
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


class log_action:
    """Декоратор для логирования доменных операций"""

    def __init__(self, action: str, verbose: bool = False):
        self.action = action.upper()
        self.verbose = verbose

    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Импортируем здесь чтобы избежать циклических импортов
            try:
                from .logging_config import action_logger
            except ImportError:
                import logging

                action_logger = logging.getLogger("domain_actions")

            # Извлекаем контекст из аргументов
            log_context = self._extract_context(args, kwargs)
            result = "OK"
            error_type = ""
            error_message = ""
            context_info = ""

            try:
                # Выполняем функцию
                return_value = func(*args, **kwargs)

                # Добавляем verbose информацию если нужно
                if self.verbose:
                    context_info = self._get_verbose_context(return_value, args, kwargs)

                return return_value

            except Exception as e:
                # Фиксируем ошибку
                result = "ERROR"
                error_type = type(e).__name__
                error_message = str(e)
                raise e

            finally:
                # Формируем дополнительные поля
                extra = {
                    "action": self.action,
                    "username": log_context.get("username", "unknown"),
                    "user_id": log_context.get("user_id", "unknown"),
                    "currency_code": log_context.get("currency_code", ""),
                    "amount": log_context.get("amount", 0),
                    "rate": log_context.get("rate", 0),
                    "base_currency": log_context.get("base_currency", ""),
                    "result": result,
                    "error_type": error_type,
                    "error_message": error_message,
                    "context": context_info,
                }

                # Логируем
                if result == "OK":
                    action_logger.info(
                        f"{self.action} operation completed", extra=extra
                    )
                else:
                    action_logger.error(f"{self.action} operation failed", extra=extra)

        return wrapper

    def _extract_context(self, args: tuple, kwargs: dict) -> dict:
        """Извлекает контекст логирования из аргументов функции"""
        from src.valutatrade_hub.infra.settings import app_config

        context = {}

        match self.action:
            case "LOGIN":
                context["username"] = args[0]
            case "REGISTER":
                context["username"] = args[0]
            case "SELL" | "BUY":
                db = args[3]

                # Извлекаем портфель
                rates = db.load(app_config.get("RATES_FILE")) or []
                try:
                    rate = utils.get_rate(
                        args[1], app_config.get("BASE_CURRENCY"), rates
                    )
                except ValueError:
                    rate = 0
                context["username"] = args[0].username if args[0] else "unknown"
                context["currency_code"] = args[1]
                context["amount"] = args[2]
                context["base_currency"] = app_config.get("BASE_CURRENCY")
                context["rate"] = rate

        return context

    def _get_verbose_context(self, return_value: Any, args: tuple, kwargs: dict) -> str:
        """Генерирует verbose контекст"""
        try:
            pass

        except Exception:
            # Игнорируем ошибки в verbose контексте
            pass

        return ""


# Фабрика декораторов
def log_domain_action(action: str, verbose: bool = False):
    """Фабрика декораторов для конкретных действий"""

    def decorator(func):
        return log_action(action, verbose)(func)

    return decorator

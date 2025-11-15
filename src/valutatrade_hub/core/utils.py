import hashlib
import json
import os
from datetime import datetime
from typing import Any

from src.valutatrade_hub import const
from src.valutatrade_hub.core import models
from src.valutatrade_hub.core.decorators import error_handler


def validate_positive_number(value: float, entity_name: str):
    """Валидация положительного числа"""
    import math

    if (not isinstance(value, float)) or math.isnan(value) or value < 0:
        raise ValueError(f"Значение {entity_name} должно быть положительным числом")

    return value


class FileStorage:
    def __init__(self, dir: str):
        """
        Инициализация хранилища данных

        Args:
            dir: директория, в которой будут сохраняться данные
        """
        self._dir = dir

    def save(self, filename: str, data: Any):
        """Сохранение данных в файл"""

        file_path = os.path.join(self._dir, filename)

        # Создаем директорию, если она не существует
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False)

        return True

    def load(self, filename: str):
        """Загрузка данных из файла"""

        try:
            with open(os.path.join(self._dir, filename), "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            print("test")
            return None


def welcome():
    """Вывод приветствия"""
    print("*" * 35)
    print("Добро пожаловать в Valutatrade Hub!")
    print("*" * 35)
    print("\n")


def hashed_password(password: str, salt: str) -> str:
    """Хеширование пароля"""
    password_salted = password + salt
    return hashlib.sha256(password_salted.encode()).hexdigest()


def generate_salt():
    """Генерация соли"""
    return hashlib.sha256(os.urandom(32)).hexdigest()


@error_handler
def parse_args(args: list[str]):
    """Парсинг аргументов командной строки"""
    result = {}
    i = 0

    while i < len(args):
        if args[i].startswith("--"):
            key = args[i][2:]  # убираем '--'
            if i + 1 < len(args) and not args[i + 1].startswith("--"):
                result[key] = args[i + 1]
                i += 2
            else:
                result[key] = None  # или можно пропустить
                i += 1
        else:
            i += 1  # пропускаем не-аргументы

    return result


def create_user(user_id: int, username: str, hashed_password: str, salt: str):
    """Создание пользователя"""
    return {
        "user_id": user_id,
        "username": username,
        "hashed_password": hashed_password,
        "salt": salt,
        "registration_date": datetime.now().isoformat(),
    }


def create_portfolio(user_id: int):
    """Создание портфеля"""
    return {
        "user_id": user_id,
        "wallets": {
            const.BASE_CURRENCY: {"balance": 0.0},
        },
    }

def get_user_portfolio(portfolios, user_id: int):
    """Получение портфеля пользователя"""

    user_portfolio = None

    for _portfolio in portfolios:
        if _portfolio["user_id"] == user_id:
            user_portfolio = models.Portfolio(
                user_id=_portfolio["user_id"],
                wallets=_portfolio["wallets"],
            )
            break

    if not user_portfolio:
        raise ValueError("Портфель не найден")

    return user_portfolio


def get_rate(from_currency: str, to_currency: str, rates):
    rate_key = f"{from_currency}_{to_currency}"

    if rate_key not in rates:
        raise ValueError(
            f"Невозможно конвертировать валюту {from_currency} в {to_currency}"
        )

    return rates[rate_key]["rate"]


def convert_currency(amount: float, from_currency: str, to_currency: str, rates):
    """Конвертирует валюту"""
    if from_currency == to_currency:
        return amount

    rate = get_rate(from_currency, to_currency, rates)

    amount *= rate

    return amount

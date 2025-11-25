from datetime import datetime
from typing import Any

from src.valutatrade_hub.core import utils
from src.valutatrade_hub.core.exceptions import InsufficientFundsError
from src.valutatrade_hub.core.utils import hashed_password, validate_positive_number
from src.valutatrade_hub.decorators import error_handler


class User:
    """Пользователь"""

    def __init__(
        self,
        user_id: int,
        username: str,
        hashed_password: str,
        salt: str,
        registration_date: datetime,
    ):
        """
        Инициализация пользователя

        Args:
            user_id: уникальный идентификатор пользователя
            username: имя пользователя
            hashed_password: захешированный пароль
            salt: соль для хеширования
            registration_date: дата регистрации в формате datetime
        """
        self._user_id = user_id
        self._username = username  # используем сеттер для проверки
        self._hashed_password = hashed_password
        self._salt = salt
        self._registration_date = registration_date

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def username(self) -> str:
        return self._username

    @username.setter
    def username(self, username: str):
        if not username or not username.strip():
            raise ValueError("Имя пользователя не может быть пустым")
        self._username = username.strip()

    @property
    def hashed_password(self) -> str:
        return self._hashed_password

    @property
    def salt(self) -> str:
        return self._salt

    @property
    def registration_date(self) -> datetime:
        return self._registration_date

    def get_user_info(self):
        """Возвращает информацию о пользователе (без пароля и соли)"""
        return {
            "user_id": self._user_id,
            "username": self._username,
            "registration_date": self._registration_date,
        }

    @error_handler
    def change_password(self, new_password: str):
        """Изменяет пароль пользователя"""
        if (
            not new_password
            or not new_password.strip()
            or len(new_password.strip()) < 4
        ):
            raise ValueError("Пароль должен содержать не менее 4 символов")

        # Хешируем новый пароль с существующей солью
        self._hashed_password = hashed_password(new_password, self._salt)
        pass

    def verify_password(self, password: str) -> bool:
        """Проверяет пароль пользователя"""
        return self._hashed_password == hashed_password(password, self._salt)


class Wallet:
    """Кошелек пользователя"""

    def __init__(self, currency_code: str, balance=0.0):
        """
        Инициализация кошелька

        Args:
            currency_code: код валюты
            balance: баланс кошелька
        """
        self._currency_code = currency_code.upper()
        self._balance = balance

    @property
    def currency_code(self):
        return self._currency_code

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, balance: float):
        self._balance = validate_positive_number(balance, "баланса")

    def deposit(self, amount: float):
        """Пополняет кошелек"""
        self._balance += validate_positive_number(amount, "суммы")

    def withdraw(self, amount: float):
        """Снимает деньги со счета"""
        if self._balance < amount:
            raise InsufficientFundsError(
                f"доступно {self._balance} {self._currency_code}, требуется {amount} {self._currency_code}"  # noqa E501
            )
        self._balance -= validate_positive_number(amount, "суммы")

    def get_balance_info(self):
        """Возвращает информацию о балансе кошелька"""
        return {
            "currency_code": self._currency_code,
            "balance": self._balance,
        }


class Portfolio:
    """Портфель пользователя"""

    def __init__(self, user_id: int, wallets: dict[str, Any]):
        """
        Инициализация портфеля

        Args:
            user_id: уникальный идентификатор пользователя
            wallets: кошельки пользователя
        """
        self._user_id = user_id
        self._wallets = wallets

    @property
    def user_id(self):
        return self._user_id

    @property
    def user(self):
        return {"user_id": self._user_id, "wallets": self._wallets}

    @property
    def wallets(self):
        return self._wallets.copy()

    def add_currency(self, currency_code: str):
        """Добавляет валюту в портфель"""

        if not currency_code:
            raise ValueError("Код валюты не может быть пустым")

        if currency_code in self._wallets:
            raise ValueError("Валюта уже добавлена в портфель")

        self._wallets[currency_code] = {"balance": 0.0}

    def get_total_value(
        self,
        rates,
        base_currency="USD",
    ):
        """Возвращает общую стоимость портфеля в указанной валюте"""

        total_value = 0.0
        for key, value in self._wallets.items():
            wallet_value = utils.convert_currency(
                value.get("balance"), key, base_currency, rates
            )

            if wallet_value is None:
                total_value = None
                break

            total_value += wallet_value

        return total_value

    def get_wallet(self, currency_code: str):
        """Возвращает кошелек пользователя по коду валюты"""

        if currency_code not in self._wallets:
            raise ValueError("Валюта не найдена в портфеле")
        return self._wallets[currency_code]

import hashlib
from datetime import datetime

from src.valutatrade_hub.core.utils import validate_positive_number


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

    def change_password(self, new_password: str):
        """Изменяет пароль пользователя"""
        if (
            not new_password
            or not new_password.strip()
            or len(new_password.strip()) < 4
        ):
            raise ValueError("Пароль должен содержать не менее 4 символов")

        # Хешируем новый пароль с существующей солью
        self._hashed_password = self._hash_password(new_password)
        pass

    def _hash_password(self, password: str) -> str:
        """Хеширует пароль с солью"""
        password_salted = password + self._salt
        return hashlib.sha256(password_salted.encode()).hexdigest()

    def verify_password(self, password: str) -> bool:
        """Проверяет пароль пользователя"""
        return self._hashed_password == self._hash_password(password)


class Wallet:
    """Кошелек пользователя"""

    def __init__(self, currency_code: str, balance=0.0):
        """
        Инициализация кошелька

        Args:
            currency_code: код валюты
            balance: баланс кошелька
        """
        self.currency_code = currency_code
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
            raise ValueError("Недостаточно средств на кошельке")
        self._balance -= validate_positive_number(amount, "суммы")

    def get_balance_info(self):
        """Возвращает информацию о балансе кошелька"""
        return {
            "currency_code": self._currency_code,
            "balance": self._balance,
        }

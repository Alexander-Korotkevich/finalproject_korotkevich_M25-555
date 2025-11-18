from abc import ABC, abstractmethod
from typing import Dict

from src.valutatrade_hub.core.exceptions import CurrencyNotFoundError


class Currency(ABC):
    """Абстрактный базовый класс для валют"""

    def __init__(self, name: str, code: str):
        self._validate_name(name)
        self._validate_code(code)
        self.name = name
        self.code = code.upper()

    def _validate_name(self, name: str):
        """Валидация имени валюты"""
        if not name or not name.strip():
            raise ValueError("Название валюты не может быть пустым")
        self.name = name.strip()

    def _validate_code(self, code: str):
        """Валидация кода валюты"""
        if not code or not code.strip():
            raise ValueError("Код валюты не может быть пустым")
        code = code.strip().upper()
        if len(code) < 2 or len(code) > 5:
            raise ValueError("Код валюты должен содержать от 2 до 5 символов")
        if " " in code:
            raise ValueError("Код валюты не может содержать пробелы")

    @abstractmethod
    def get_display_info(self) -> str:
        """Возвращает строковое представление для UI/логов"""
        pass


class FiatCurrency(Currency):
    """Фиатная валюта"""

    def __init__(self, name: str, code: str, issuing_country: str):
        super().__init__(name, code)
        self._validate_issuing_country(issuing_country)
        self.issuing_country = issuing_country

    def _validate_issuing_country(self, country: str):
        """Валидация страны эмитента"""
        if not country or not country.strip():
            raise ValueError("Страна эмитент не может быть пустой")
        self.issuing_country = country.strip()

    def get_display_info(self) -> str:
        """Возвращает строковое представление фиатной валюты"""
        return f"[FIAT] {self.code} — {self.name} (Issuing: {self.issuing_country})"


class CryptoCurrency(Currency):
    """Криптовалюта"""

    def __init__(self, name: str, code: str, algorithm: str, market_cap: float = 0.0):
        super().__init__(name, code)
        self._validate_algorithm(algorithm)
        self._validate_market_cap(market_cap)
        self.algorithm = algorithm
        self.market_cap = market_cap

    def _validate_algorithm(self, algorithm: str):
        """Валидация алгоритма"""
        if not algorithm or not algorithm.strip():
            raise ValueError("Алгоритм не может быть пустым")
        self.algorithm = algorithm.strip()

    def _validate_market_cap(self, market_cap: float):
        """Валидация рыночной капитализации"""
        if market_cap < 0:
            raise ValueError("Рыночная капитализация не может быть отрицательной")
        self.market_cap = market_cap

    def get_display_info(self) -> str:
        """Возвращает строковое представление криптовалюты"""
        # Форматируем капитализацию в читаемом виде
        if self.market_cap >= 1e12:
            mcap_str = f"{self.market_cap/1e12:.2f}T"
        elif self.market_cap >= 1e9:
            mcap_str = f"{self.market_cap/1e9:.2f}B"
        elif self.market_cap >= 1e6:
            mcap_str = f"{self.market_cap/1e6:.2f}M"
        else:
            mcap_str = f"{self.market_cap:.2f}"

        return f"[CRYPTO] {self.code} — {self.name} (Algo: {self.algorithm}, MCAP: {mcap_str})" # noqa E501


# Реестр валют
_currency_registry: Dict[str, Currency] = {}


def register_currency(currency: Currency):
    """Регистрирует валюту в реестре"""
    _currency_registry[currency.code] = currency


def get_currency(code: str) -> Currency:
    """Возвращает валюту по коду"""
    code = code.strip().upper()
    if code not in _currency_registry:
        raise CurrencyNotFoundError(f"Неизвестная валюта '{code}'")
    return _currency_registry[code]


def get_all_currencies() -> Dict[str, Currency]:
    """Возвращает все зарегистрированные валюты"""
    return _currency_registry.copy()


# Предзаполнение реестра популярными валютами
def _initialize_currencies():
    """Инициализация реестра популярными валютами"""

    # Фиатные валюты
    fiats = [
        FiatCurrency("US Dollar", "USD", "United States"),
        FiatCurrency("Euro", "EUR", "Eurozone"),
        FiatCurrency("Russian Ruble", "RUB", "Russia"),
    ]

    # Криптовалюты
    cryptos = [
        CryptoCurrency("Bitcoin", "BTC", "SHA-256", 1.12e12),
        CryptoCurrency("Ethereum", "ETH", "Ethash", 4.5e11),
    ]

    # Регистрация всех валют
    for currency in fiats + cryptos:
        register_currency(currency)


# Инициализируем реестр при импорте
_initialize_currencies()

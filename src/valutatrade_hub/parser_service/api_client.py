from abc import ABC, abstractmethod
from typing import Dict

import requests

from src.valutatrade_hub.core.exceptions import (
    ApiKeyError,
    ApiRequestError,
    NetworkError,
    RateLimitError,
)
from src.valutatrade_hub.infra.settings import app_config
from src.valutatrade_hub.parser_service.config import parser_config


class BaseApiClient(ABC):
    """Абстрактный базовый класс для API клиентов"""

    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()

    @abstractmethod
    def fetch_rates(self) -> Dict[str, float]:
        """
        Получает актуальные курсы валют

        Returns:
            Словарь в формате {"BTC_USD": 59337.21, "EUR_USD": 1.085, ...}

        Raises:
            ApiRequestError: при ошибках сети или API
        """
        pass

    def _make_request(self, url: str, params: Dict | None = None) -> Dict:
        """
        Выполняет HTTP запрос с обработкой ошибок

        Args:
            url: URL для запроса
            params: параметры запроса

        Returns:
            Ответ API в виде словаря

        Raises:
            ApiRequestError: при ошибках сети или API
        """
        try:
            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout,
                headers={"User-Agent": "ValutaTradeHub/1.0"},
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout as e:
            raise NetworkError(f"Request timeout: {e}", url=url)

        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection error: {e}", url=url)

        except requests.exceptions.HTTPError as e:
            status_code = response.status_code
            if status_code == 401:
                raise ApiKeyError(f"Invalid API key: {e}", status_code, url)
            elif status_code == 429:
                raise RateLimitError(f"Rate limit exceeded: {e}", status_code, url)
            else:
                raise ApiRequestError(
                    f"HTTP error {status_code}: {e}", status_code, url
                )

        except requests.exceptions.RequestException as e:
            raise ApiRequestError(f"Request failed: {e}", url=url)

        except ValueError as e:
            raise ApiRequestError(f"Invalid JSON response: {e}", url=url)


class CoinGeckoClient(BaseApiClient):
    """API клиент для CoinGecko"""

    def __init__(
        self,
        base_url: str = parser_config.COINGECKO_URL,
        vs_currency: str = app_config.get("BASE_CURRENCY"),
        timeout: int = 10,
    ):
        super().__init__(base_url, timeout)
        self.crypto_ids = parser_config.CRYPTO_ID_MAP
        self.vs_currency = vs_currency.lower()

    def fetch_rates(self) -> Dict[str, float]:
        """
        Получает курсы криптовалют от CoinGecko

        Returns:
            Словарь в формате {"BTC_USD": 59337.21, "ETH_USD": 3850.75, ...}
        """
        if not self.crypto_ids:
            raise ApiRequestError("No cryptocurrency IDs configured")

        # Формируем параметры запроса
        params = {
            "ids": ",".join(self.crypto_ids.values()),
            "vs_currencies": self.vs_currency,
        }

        # Выполняем запрос
        data = self._make_request(self.base_url, params)

        # Преобразуем ответ в стандартный формат
        return self._parse_response(data)

    def _parse_response(self, data: Dict) -> Dict[str, float]:
        """Парсит ответ CoinGecko в стандартный формат"""
        rates = {}

        for crypto_symbol, crypto_id in self.crypto_ids.items():
            if crypto_id in data and self.vs_currency in data[crypto_id]:
                rate = data[crypto_id][self.vs_currency]
                key = f"{crypto_symbol}_{self.vs_currency.upper()}"
                rates[key] = float(rate)

        if not rates:
            raise ApiRequestError("No rates found in API response")

        return rates


class ExchangeRateApiClient(BaseApiClient):
    """API клиент для ExchangeRate-API"""

    def __init__(
        self,
        api_key=parser_config.EXCHANGERATE_API_KEY,
        base_url: str = parser_config.EXCHANGERATE_API_URL,
        base_currency: str = app_config.get("BASE_CURRENCY"),
        timeout: int = 10,
    ):
        if not api_key:
            raise ApiKeyError("API key is required for ExchangeRate-API")

        super().__init__(base_url, timeout)
        self.api_key = api_key
        self.base_currency = base_currency.upper()

    def fetch_rates(self) -> Dict[str, float]:
        """
        Получает курсы фиатных валют от ExchangeRate-API

        Returns:
            Словарь в формате {"EUR_USD": 1.085, "GBP_USD": 1.275, ...}
        """
        # Формируем URL с API ключом
        url = f"{self.base_url}/{self.api_key}/latest/{self.base_currency}"

        # Выполняем запрос
        data = self._make_request(url)

        # Проверяем статус ответа API
        if data.get("result") != "success":
            error_type = data.get("error-type", "unknown_error")
            raise ApiRequestError(f"API error: {error_type}")

        # Преобразуем ответ в стандартный формат
        return self._parse_response(data)

    def _parse_response(self, data: Dict) -> Dict[str, float]:
        """Парсит ответ ExchangeRate-API в стандартный формат"""
        rates = {}

        conversion_rates = data.get("conversion_rates", {})

        for currency, rate in conversion_rates.items():
            if currency != self.base_currency:
                key = f"{currency}_{self.base_currency}"
                rates[key] = float(rate)

        if not rates:
            raise ApiRequestError("No conversion rates found in API response")

        return rates

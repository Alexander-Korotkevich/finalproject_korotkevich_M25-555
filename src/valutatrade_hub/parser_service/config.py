import os
from dataclasses import dataclass, field
from typing import Dict

from dotenv import load_dotenv

load_dotenv()  # ← это обязательно!


@dataclass
class ParserConfig:
    # Ключ загружается из переменной окружения
    EXCHANGERATE_API_KEY: str | None = os.getenv("EXCHANGERATE_API_KEY")

    # Эндпоинты
    COINGECKO_URL: str = "https://api.coingecko.com/api/v3/simple/price"
    EXCHANGERATE_API_URL: str = "https://v6.exchangerate-api.com/v6"

    # Списки валют
    BASE_CURRENCY: str = "USD"
    FIAT_CURRENCIES: tuple = ("EUR", "GBP", "RUB")
    CRYPTO_CURRENCIES: tuple = ("BTC", "ETH", "SOL")

    CRYPTO_ID_MAP: Dict[str, str] = field(
        default_factory=lambda: {
            "BTC": "bitcoin",
            "ETH": "ethereum",
        }
    )

    # Пути
    RATES_FILE_PATH: str = "rates.json"
    HISTORY_FILE_PATH: str = "exchange_rates.json"

    # Сетевые параметры
    REQUEST_TIMEOUT: int = 10

parser_config = ParserConfig()

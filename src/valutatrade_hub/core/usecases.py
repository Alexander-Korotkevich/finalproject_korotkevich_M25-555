import src.valutatrade_hub.const as const
import src.valutatrade_hub.core.utils as utils
from src.valutatrade_hub.core import currencies, models
from src.valutatrade_hub.core.exceptions import InsufficientFundsError
from src.valutatrade_hub.decorators import check_auth, error_handler, log_domain_action
from src.valutatrade_hub.infra.database import DatabaseManager
from src.valutatrade_hub.infra.settings import app_config
from src.valutatrade_hub.parser_service import updater
from src.valutatrade_hub.parser_service.api_client import (
    CoinGeckoClient,
    ExchangeRateApiClient,
)
from src.valutatrade_hub.parser_service.storage import Storage


def exit():
    """Выход из программы"""
    print("Выход из программы")
    return False


@error_handler
@log_domain_action(const.LOG_ACTION_REGISTER)
def register(username: str | None, password: str | None, db: DatabaseManager):
    """Регистрация нового пользователя"""

    if (not username or not password) or not username.strip() or not password.strip():
        raise ValueError("Пожалуйста, введите имя пользователя и пароль")

    if len(password.strip()) < const.MIN_PASSWORD_LENGTH:
        raise ValueError(
            f"Пароль должен содержать не менее {const.MIN_PASSWORD_LENGTH} символов"
        )

    users = db.load(app_config.get("USERS_FILE")) or []

    if users and any(user["username"] == username for user in users):
        raise ValueError(f"Имя пользователя '{username}' уже занято")

    # Создаем нового пользователя
    id = len(users) + 1
    salt = utils.generate_salt()
    hashed_password = utils.hashed_password(password, salt)
    user = utils.create_user(id, username, hashed_password, salt)
    users.append(user)
    result = db.save(app_config.get("USERS_FILE"), users)

    # Создаем портфель
    portfolios = db.load(app_config.get("PORTFOLIOS_FILE")) or []
    portfolio = utils.create_portfolio(id, app_config.get("BASE_CURRENCY"))
    portfolios.append(portfolio)
    db.save(app_config.get("PORTFOLIOS_FILE"), portfolios)

    if result:
        print(
            f"Пользователь '{username}' зарегистрирован (id={id}).",
            f"Войдите: login --username {username} --password **** ",
        )
    else:
        raise RuntimeError("Произошла ошибка при сохранении данных")


@error_handler
@log_domain_action(const.LOG_ACTION_LOGIN)
def login(username: str | None, password: str | None, db: DatabaseManager):
    """Вход в систему"""

    if (not username or not password) or not username.strip() or not password.strip():
        raise ValueError("Пожалуйста, введите имя пользователя и пароль")

    users = db.load(app_config.get("USERS_FILE")) or []

    current_user = None

    for user in users:
        if user["username"] == username:
            current_user = user
            break

    if not current_user:
        raise ValueError(f"Пользователь '{username}' не найден")

    hashed_password = utils.hashed_password(password, current_user["salt"])

    if current_user["hashed_password"] != hashed_password:
        raise ValueError("Неверный пароль")

    print(f"Вы вошли как '{username}'")

    return models.User(
        user_id=current_user["user_id"],
        username=current_user["username"],
        hashed_password=current_user["hashed_password"],
        salt=current_user["salt"],
        registration_date=current_user["registration_date"],
    )


@error_handler
@check_auth
def show_portfolio(
    user: models.User, db, base_currency=app_config.get("BASE_CURRENCY")
):
    """Показать портфель"""

    portfolios = db.load(app_config.get("PORTFOLIOS_FILE")) or []
    user_portfolio = utils.get_user_portfolio(
        portfolios, user.user_id, models.Portfolio
    )

    if not user_portfolio.wallets:
        raise ValueError("В портфеле нет кошельков")

    if base_currency not in const.CURRENCY:
        raise ValueError(f"Неизвестная базовая валюта '{base_currency}'")

    rates = db.load(app_config.get("RATES_FILE")) or {}
    pairs = rates.get("pairs") or {}

    print(f"Портфель пользователя '{user.username}' (база: {base_currency}):")

    for key, value in user_portfolio.wallets.items():
        converted_currency = utils.convert_currency(
            value.get("balance"), key, base_currency, pairs
        )
        if converted_currency is not None:
            print(
                f"- {key}: {value.get("balance")}  → {converted_currency} {base_currency}"  # noqa E501
            )

    print("---------------------------------")

    total_value = user_portfolio.get_total_value(pairs, base_currency)

    if total_value is not None:
        print(f"ИТОГО: {total_value} {base_currency}")


@error_handler
@log_domain_action(const.LOG_ACTION_BUY)
@check_auth
def buy(user: models.User, currency: str, amount: float, db):
    """Купить валюту"""

    currencies.get_currency(currency)

    utils.validate_positive_number(amount, "количества валюты", no_zero=True)

    portfolios = db.load(app_config.get("PORTFOLIOS_FILE")) or []
    user_portfolio = utils.get_user_portfolio(
        portfolios, user.user_id, models.Portfolio
    )

    if currency not in user_portfolio.wallets:
        user_portfolio.add_currency(currency)

    cur_wallet_data = user_portfolio.get_wallet(currency)
    usd_wallet_data = user_portfolio.get_wallet(app_config.get("BASE_CURRENCY"))

    rates = db.load(app_config.get("RATES_FILE")) or {}
    pairs = rates.get("pairs") or {}
    usd_amount = utils.convert_currency(
        amount, currency, app_config.get("BASE_CURRENCY"), pairs
    )

    if usd_amount is None:
        raise ValueError(f"Невозможно приобрести {amount} {currency}")

    if usd_wallet_data.get("balance") < usd_amount:
        raise InsufficientFundsError(f"для приобретения {amount} {currency}")

    usd_wallet = models.Wallet(
        app_config.get("BASE_CURRENCY"), usd_wallet_data.get("balance")
    )
    usd_wallet.withdraw(usd_amount)

    cur_wallet = models.Wallet(currency, cur_wallet_data.get("balance"))
    cur_wallet.deposit(amount)

    rate = utils.get_rate(currency, app_config.get("BASE_CURRENCY"), pairs)

    for _portfolio in portfolios:
        if _portfolio.get("user_id") == user.user_id:
            _portfolio.get("wallets")[currency] = {"balance": cur_wallet.balance}
            _portfolio.get("wallets")[app_config.get("BASE_CURRENCY")] = {
                "balance": usd_wallet.balance
            }
            break

    db.save(app_config.get("PORTFOLIOS_FILE"), portfolios)

    print(
        f"Покупка выполнена: {amount} {currency} по курсу {rate} {app_config.get("BASE_CURRENCY")}/{currency}"  # noqa E501
    )
    print("Изменения в портфеле:")
    print(
        f"- {currency}: было {cur_wallet_data.get('balance')} → стало {cur_wallet.balance}"  # noqa E501
    )
    print(f"Оценочная стоимость покупки: {usd_amount} USD")


@error_handler
@log_domain_action(const.LOG_ACTION_SELL)
@check_auth
def sell(user: models.User, currency: str, amount: float, db: DatabaseManager):
    """Продать валюту"""

    currencies.get_currency(currency)

    utils.validate_positive_number(amount, "количества валюты", no_zero=True)

    portfolios = db.load(app_config.get("PORTFOLIOS_FILE")) or []
    user_portfolio = utils.get_user_portfolio(
        portfolios, user.user_id, models.Portfolio
    )

    try:
        cur_wallet_data = user_portfolio.get_wallet(currency)
    except ValueError:
        raise ValueError(
            f"У вас нет кошелька '{currency}'. Добавьте валюту: она создаётся автоматически при первой покупке."  # noqa E501
        )

    usd_wallet_data = user_portfolio.get_wallet(app_config.get("BASE_CURRENCY"))

    if cur_wallet_data.get("balance") < amount:
        raise InsufficientFundsError(
            f"доступно {cur_wallet_data.get("balance")} {currency}, требуется {amount} {currency}"  # noqa E501
        )

    cur_wallet = models.Wallet(currency, cur_wallet_data.get("balance"))
    cur_wallet.withdraw(amount)

    rates = db.load(app_config.get("RATES_FILE")) or {}
    pairs = rates.get("pairs")
    rate = utils.get_rate(currency, app_config.get("BASE_CURRENCY"), pairs)

    usd_amount = utils.convert_currency(
        amount, currency, app_config.get("BASE_CURRENCY"), pairs
    )

    usd_wallet = models.Wallet(
        app_config.get("BASE_CURRENCY"), usd_wallet_data.get("balance")
    )
    usd_wallet.withdraw(usd_amount)

    for _portfolio in portfolios:
        if _portfolio.get("user_id") == user.user_id:
            _portfolio.get("wallets")[currency] = {"balance": cur_wallet.balance}
            _portfolio.get("wallets")[app_config.get("BASE_CURRENCY")] = {
                "balance": usd_wallet.balance
            }
            break

    db.save(app_config.get("PORTFOLIOS_FILE"), portfolios)

    print(
        f"Продажа выполнена: {amount} {currency} по курсу {rate} {app_config.get("BASE_CURRENCY")}/{currency}"  # noqa E501
    )
    print("Изменения в портфеле:")
    print(
        f"- {currency}: было {cur_wallet_data.get('balance')} → стало {cur_wallet.balance}"  # noqa E501
    )
    print(f"Оценочная выручка: {usd_amount} USD")

@error_handler
def update_rates(source: str | None, db: DatabaseManager):

    clients = []
        
    match source:
        case "coingecko":
            clients = [CoinGeckoClient()]
        case "exchangerate":
            clients = [ExchangeRateApiClient()]    
        case _:
            clients = [CoinGeckoClient(), ExchangeRateApiClient()]   
        
    storage = Storage(db)
    rates_updater = updater.RatesUpdater(clients, storage)
    rates_updater.run_update()

@error_handler
def get_rate_action(
    from_currency: str | None, to_currency: str | None, db: DatabaseManager
):
    if (from_currency not in const.CURRENCY) or (to_currency not in const.CURRENCY):
        raise ValueError(
            f"Невозможно конвертировать валюту {from_currency} в {to_currency}"
        )

    rates = db.load(app_config.get("RATES_FILE")) or {}
    pairs = rates.get("pairs") or {}
    rate_key = f"{from_currency}_{to_currency}"
    rate_data = pairs.get(rate_key) or {}
    is_old = utils.is_old_update(
        rate_data.get("updated_at"), app_config.get("RATES_TTL_SECONDS")
    )

    if not pairs or is_old:
        update_rates(None, db)
        get_rate_action(from_currency, to_currency, db)
        return

    print(
        f"Курс {rate_key}: {rate_data.get('rate')} (обновлено: {rate_data.get("updated_at")})"  # noqa E501
    )
    print("Обратный курс BTC→USD: 59337.21")  # TODO:


@error_handler
def show_rates(currency_filter: str | None, top_filter: int | None, base_currency: str | None, db: DatabaseManager): # noqa E501
    rates = db.load(app_config.get("RATES_FILE")) or {}
    pairs = rates.get("pairs") or {}

    if not pairs:
        print("Файл кеша пуст или не найден →")
        print(f"Локальный кеш курсов пуст. Выполните '{const.CMD_UPDATE_RATES}', чтобы загрузить данные.") # noqa E501
    
    if currency_filter:
        pairs = {key: value for key, value in pairs.items() if key.startswith(currency_filter)} # noqa E501

        if not pairs:
            raise ValueError(f"\nВалюта не найдена →\nКурс для '{currency_filter}' не найден в кеше.") # noqa E501

    if top_filter:
        pairs = dict(sorted(pairs.items(), key=lambda item: item[1].get("rate"), reverse=True)[:top_filter])  # noqa E501
        print(f"Rates from cache (updated at {pairs.get('last_refresh')}):")

    if base_currency:
        pairs = {key: value for key, value in pairs.items() if key.endswith(base_currency)}  # noqa E501    

    for key, value in pairs.items():
        print(f"- {key}: {value.get('rate')}")

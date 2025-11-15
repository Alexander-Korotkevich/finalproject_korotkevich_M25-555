from datetime import datetime
import os
import src.valutatrade_hub.const as const
from src.valutatrade_hub.core import models
from src.valutatrade_hub.core.decorators import error_handler
import src.valutatrade_hub.core.utils as utils

current_dir = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.dirname(current_dir)
storage_path = os.path.join(root_path, const.DATA_DIR)
storage = utils.FileStorage(storage_path)


def exit():
    """Выход из программы"""
    print("Выход из программы")
    return False


@error_handler
def register(username: str | None, password: str | None):
    """Регистрация нового пользователя"""

    if (not username or not password) or not username.strip() or not password.strip():
        raise ValueError("Пожалуйста, введите имя пользователя и пароль")

    if len(password.strip()) < const.MIN_PASSWORD_LENGTH:
        raise ValueError(
            f"Пароль должен содержать не менее {const.MIN_PASSWORD_LENGTH} символов"
        )

    users = storage.load(const.USERS_FILE) or []

    if users and any(user["username"] == username for user in users):
        raise ValueError(f"Имя пользователя '{username}' уже занято")

    # Создаем нового пользователя
    id = len(users) + 1
    salt = utils.generate_salt()
    hashed_password = utils.hashed_password(password, salt)
    user = utils.create_user(id, username, hashed_password, salt)
    users.append(user)
    result = storage.save(const.USERS_FILE, users)

    # Создаем портфель
    portfolios = storage.load(const.PORTFOLIOS_FILE) or []
    portfolio = utils.create_portfolio(id)
    portfolios.append(portfolio)
    storage.save(const.PORTFOLIOS_FILE, portfolios)

    if result:
        print(
            f"Пользователь '{username}' зарегистрирован (id={id}).",
            f"Войдите: login --username {username} --password **** ",
        )
    else:
        raise RuntimeError("Произошла ошибка при сохранении данных")


@error_handler
def login(username: str | None, password: str | None):
    """Вход в систему"""

    if (not username or not password) or not username.strip() or not password.strip():
        raise ValueError("Пожалуйста, введите имя пользователя и пароль")

    users = storage.load(const.USERS_FILE) or []

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

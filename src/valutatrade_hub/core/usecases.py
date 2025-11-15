from datetime import datetime
import os
import src.valutatrade_hub.const as const
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

    users = storage.load("users.json") or []

    if users and any(user["username"] == username for user in users):
        raise ValueError(f"Имя пользователя '{username}' уже занято")

    id = len(users) + 1
    salt = utils.generate_salt()

    user = {
        "user_id": id,
        "username": username,
        "hashed_password": utils.hashed_password(password, salt),
        "salt": salt,
        "registration_date": datetime.now().isoformat(),
    }

    users.append(user)

    result = storage.save("users.json", users)

    if result:
        print(
            f"Пользователь '{username}' зарегистрирован (id={id}).",
            f"Войдите: login --username {username} --password **** ",
        )

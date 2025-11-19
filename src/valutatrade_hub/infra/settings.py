import json
import os
from src.valutatrade_hub.core.utils import SingletonMeta
import sys


class SettingsLoader(metaclass=SingletonMeta):
    """Класс для загрузки конфигурационного файла"""

    # Путь к конфигурационному файлу
    _config_path = "src/config.json"

    def __init__(self):
        self._config = self._load_config()

    def _load_config(self):
        """Загрузка конфигурационного файла"""
        try:
            with open(os.path.abspath(self._config_path), "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Конфигурационный файл не найден")
            sys.exit()

    def get(self, key: str):
        """Получение значения из конфигурационного файла"""
        if not self._config:
            raise RuntimeError("Конфигурационный файл не загружен")

        if key not in self._config:
            raise KeyError(f"'{key}' в конфигурационном файле")

        return self._config.get(key)


app_config = SettingsLoader()

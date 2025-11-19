import json
import os
from typing import Any


class DatabaseManager:
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
            return None

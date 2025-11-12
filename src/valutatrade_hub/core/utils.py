import json
import os


def validate_positive_number(value: float, entity_name: str):
    """Валидация положительного числа"""
    import math

    if (not isinstance(value, float)) or math.isnan(value) or value < 0:
        raise ValueError(f"Значение {entity_name} должно быть положительным числом")

    return value


class FileStorage:
    def __init__(self, dir: str):
        """
        Инициализация хранилища данных

        Args:
            dir: директория, в которой будут сохраняться данные
        """
        self._dir = dir

    def save(self, filename: str, content: str):
        """Сохранение данных в файл"""
        with open(os.path.join(self._dir, filename), "w") as file:
            file.write(content)

    def load(self, filename: str):
        """Загрузка данных из файла"""

        try:
            with open(os.path.join(self._dir, filename), "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
        except Exception as e:
            raise Exception(f"Неожиданная ошибка: {e}")

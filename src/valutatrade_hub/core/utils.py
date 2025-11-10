def validate_positive_number(value: float, entity_name: str):
    """Валидация положительного числа"""
    import math

    if (not isinstance(value, float)) or math.isnan(value) or value < 0:
        raise ValueError(f"Значение {entity_name} должно быть положительным числом")

    return value

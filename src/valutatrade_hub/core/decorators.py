def error_handler(func):
  def wrapper(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except ValueError as e:
      print(f"Ошибка валидации: {e}")
    except Exception as e:
      print(f"Неожиданная ошибка: {e}")

  return wrapper

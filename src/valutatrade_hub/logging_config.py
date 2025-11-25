import logging
import logging.handlers
from pathlib import Path
import json

from src.valutatrade_hub.const import LOG_ACTION_API

def setup_action_logger():
    """Настройка логгера для доменных операций"""

    # Создаем директорию для логов
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Создаем логгер
    logger = logging.getLogger("domain_actions")
    logger.setLevel(logging.INFO)

    # Форматтер в JSON
    class JsonFormatter(logging.Formatter):
        def format(self, record):
            log_data = {}
            action = getattr(record, "action", "UNKNOWN")

            if action == LOG_ACTION_API:
                log_data = {
                  "timestamp": self.formatTime(record),
                  "level": record.levelname,
                  "action": action,
                  "message": record.getMessage(),
                }
            else:
              log_data = {
                  "timestamp": self.formatTime(record),
                  "level": record.levelname,
                  "action": getattr(record, "action", "UNKNOWN"),
                  "username": getattr(record, "username", "unknown"),
                  "user_id": getattr(record, "user_id", "unknown"),
                  "currency_code": getattr(record, "currency_code", ""),
                  "amount": getattr(record, "amount", 0),
                  "rate": getattr(record, "rate", 0),
                  "base_currency": getattr(record, "base_currency", ""),
                  "result": getattr(record, "result", "UNKNOWN"),
                  "error_type": getattr(record, "error_type", ""),
                  "error_message": getattr(record, "error_message", ""),
                  "context": getattr(record, "context", ""),
                  "module": record.name,
                  "function": record.funcName,
              }

            return json.dumps(log_data)

    # Форматтер для человекочитаемого вывода
    class HumanFormatter(logging.Formatter):
        def format(self, record):
            action = getattr(record, "action", "UNKNOWN")

            if action == LOG_ACTION_API:
                return f"{record.levelname} {self.formatTime(record, '%Y-%m-%dT%H:%M:%S')} {record.getMessage()}"
            else:

              currency_code = getattr(record, "currency_code", False)
              currency_code_message = (
                  f"currency='{getattr(record, 'currency_code', '')}' "
                  if currency_code
                  else ""
              )
              amount = getattr(record, "amount", 0)
              amount_message = f"amount={amount:.4f} " if amount else ""
              rate = getattr(record, "rate", 0)
              rate_message = f"rate={rate:.2f} " if rate else ""
              base = getattr(record, "base_currency", "")
              base_message = f"base='{base}' " if base else ""

              # Базовые поля
              base_message = (
                  f"{record.levelname} {self.formatTime(record, '%Y-%m-%dT%H:%M:%S')} "
                  + f"{getattr(record, 'action', 'UNKNOWN')} "
                  + f"user='{getattr(record, 'username', 'unknown')}' "
                  + currency_code_message
                  + amount_message
                  + rate_message
                  + base_message
                  + f"result={getattr(record, 'result', 'UNKNOWN')}"
              )

              # Добавляем информацию об ошибке если есть
              error_type = getattr(record, "error_type", "")
              error_message = getattr(record, "error_message", "")
              if error_type:
                  base_message += f" error={error_type}:{error_message}"

              # Добавляем контекст если есть
              context = getattr(record, "context", "")
              if context:
                  base_message += f" {context}"

              return base_message

    # File handler с ротацией (JSON формат)
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "actions.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(JsonFormatter())

    # Console handler (человекочитаемый формат)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(HumanFormatter())

    # Добавляем обработчики
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Предотвращаем дублирование логов
    logger.propagate = False

    return logger


# Инициализация при импорте
action_logger = setup_action_logger()

from datetime import datetime
from src.valutatrade_hub.parser_service.config import parser_config

class Storage():
  """Класс для сохранения курсов валют в базу данных"""
  def __init__(self, db):
    self.db = db
    
  def save_rates(self, rates):
    """Сохраняет курсы валют в базу данных"""
    rates_data = self.db.load(parser_config.RATES_FILE_PATH) or {}

    rates_data['pairs'] = rates
    rates_data['last_refresh'] = datetime.now().isoformat()

    self.db.save(parser_config.RATES_FILE_PATH, rates_data)

  def save_rates_history(self, rates):
    """Сохраняет историю курсов валют в базу данных"""
    rates_history_data = self.db.load(parser_config.HISTORY_FILE_PATH) or []

    for key, value in rates.items():
      timestamp = datetime.now().isoformat()
      [first, second] = key.split("_")
      rates_history_data.append(
        {
        "id": f"{key}_{timestamp}",
        "from_currency": first,
        "to_currency": second,
        "rate": value.get("rate"),
        "timestamp": timestamp,
        "source": value.get("source"),
      })


    self.db.save(parser_config.HISTORY_FILE_PATH, rates_history_data)

from datetime import datetime

from src.valutatrade_hub.const import LOG_ACTION_API
from src.valutatrade_hub.core.currencies import get_all_currencies
from src.valutatrade_hub.logging_config import action_logger

class RatesUpdater():
  """
  Класс для обновления курсов валют
  """

  def __init__(self, clients: list, storage):
    self.clients = clients
    self.storage = storage


  def run_update(self):
    """Запускает обновление курсов валют"""

    result = {}
    currencies_code = list(get_all_currencies().keys())

    for client in self.clients:
      try:
        action_logger.info(f"Fetching rates from {client.__class__.__name__}...", extra={'action': LOG_ACTION_API})

        res = client.fetch_rates()
        
        action_logger.info(f"Saving rates from {client.__class__.__name__}...", extra={'action': LOG_ACTION_API})

        for key, value in res.items():
          pair_key = key.split("_")[0]
          if pair_key in currencies_code:
            result[key] = {
              "rate": value,
              "source": client.__class__.__name__,
              "updated_at": datetime.now().isoformat()
            }

      except Exception as e:
        print(e)
        action_logger.error(f"Failed to fetch rates from {client.__class__.__name__}: {e}", extra={'action': LOG_ACTION_API})
        continue
          
    
    print(result)    

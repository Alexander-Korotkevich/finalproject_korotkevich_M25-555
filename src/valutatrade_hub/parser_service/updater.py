from datetime import datetime

from src.valutatrade_hub.const import LOG_ACTION_API
from src.valutatrade_hub.core.currencies import get_all_currencies
from src.valutatrade_hub.logging_config import action_logger
from src.valutatrade_hub.parser_service.storage import Storage


class RatesUpdater():
  """
  Класс для обновления курсов валют
  """

  def __init__(self, clients: list, storage: Storage):
    self.clients = clients
    self.storage = storage


  def run_update(self):
    """Запускает обновление курсов валют"""

    result = {}
    currencies_code = list(get_all_currencies().keys())

    action_logger.info("Starting rates update...", extra={'action': LOG_ACTION_API})

    for client in self.clients:
      try:

        res = client.fetch_rates()
        action_logger.info(
          f"Fetching rates from {client.__class__.__name__}... OK ({len(res)} rates)", extra={'action': LOG_ACTION_API} # noqa E501
          ) 

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
        action_logger.error(f"Failed to fetch rates from {client.__class__.__name__}: {e}", extra={'action': LOG_ACTION_API}) # noqa E501
        continue   

    self.storage.save_rates(result)
    action_logger.info(f"Writing {len(result)} rates to data/rates.json...", extra={'action': LOG_ACTION_API}) # noqa E501
    self.storage.save_rates_history(result)  
    action_logger.info(f"Update successful. Total rates updated: {len(result)}. Last refresh: {datetime.now().isoformat()}", extra={'action': LOG_ACTION_API}) # noqa E501

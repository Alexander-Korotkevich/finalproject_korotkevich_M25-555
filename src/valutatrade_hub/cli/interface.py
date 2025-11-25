import os
import shlex

import prompt  # type: ignore

import src.valutatrade_hub.const as const
import src.valutatrade_hub.core.usecases as usecases
import src.valutatrade_hub.core.utils as utils
from src.valutatrade_hub.core import models
from src.valutatrade_hub.infra.database import DatabaseManager
from src.valutatrade_hub.infra.settings import app_config

data_file_path = os.path.abspath(app_config.get("DATA_FILE"))
db = DatabaseManager(data_file_path)


def run():
    """Запуск интерфейса командной строки"""
    is_active = True
    user: models.User | None = None

    utils.welcome()

    while is_active:
        user_input = prompt.string(">>> ")
        args = shlex.split(user_input)
        command = args[0]
        command_args = utils.parse_args(args) or {}

        match (command):
            case const.CMD_REGISTER:
                usecases.register(
                    command_args.get(const.KEY_WORD_USERNAME),
                    command_args.get(const.KEY_WORD_PASSWORD),
                    db,
                )
            case const.CMD_LOGIN:
                user = usecases.login(
                    command_args.get(const.KEY_WORD_USERNAME),
                    command_args.get(const.KEY_WORD_PASSWORD),
                    db,
                )
            case const.CMD_SHOW_PORTFOLIO:
                base_currency = command_args.get(const.KEY_WORD_BASE)
                if base_currency:
                    usecases.show_portfolio(
                        user, db, base_currency
                    )
                else:
                    usecases.show_portfolio(user, db)
            case const.CMD_BUY:
                usecases.buy(
                    user,
                    command_args.get(const.KEY_WORD_CURRENCY),
                    float(command_args.get(const.KEY_WORD_AMOUNT) or 0),
                    db,
                )
            case const.CMD_SELL:
                usecases.sell(
                    user,
                    command_args.get(const.KEY_WORD_CURRENCY),
                    float(command_args.get(const.KEY_WORD_AMOUNT) or 0),
                    db,
                )
            case const.CMD_GET_RATE:
                usecases.get_rate_action(
                    command_args.get(const.KEY_WORD_FROM),
                    command_args.get(const.KEY_WORD_TO),
                    db,
                )
            case const.CMD_UPDATE_RATES:
                usecases.update_rates(command_args.get(const.KEY_WORD_SOURCE), db=db)   
            case const.CMD_SHOW_RATES:
                usecases.show_rates(command_args.get(const.KEY_WORD_CURRENCY), 
                                    int(command_args.get(const.KEY_WORD_TOP) or 0), 
                                    command_args.get(const.KEY_WORD_BASE), db=db)
                
            case const.CMD_HELP:
                usecases.help()    
            case const.CMD_EXIT:
                is_active = usecases.exit()
                continue
            case _:
                print(f"Неизвестная команда {command}")
                continue

import shlex

import prompt  # type: ignore

import src.valutatrade_hub.const as const
import src.valutatrade_hub.core.usecases as usecases
import src.valutatrade_hub.core.utils as utils
from src.valutatrade_hub.core import models


def run():
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
                )
            case const.CMD_LOGIN:
                user = usecases.login(
                    command_args.get(const.KEY_WORD_USERNAME),
                    command_args.get(const.KEY_WORD_PASSWORD),
                )
            case const.CMD_SHOW_PORTFOLIO:
                base_currency = command_args.get(const.KEY_WORD_BASE)
                if base_currency:
                    usecases.show_portfolio(user, command_args.get(const.KEY_WORD_BASE))
                else:
                    usecases.show_portfolio(user)
            case const.CMD_BUY:
                usecases.buy(
                    user,
                    command_args.get(const.KEY_WORD_CURRENCY),
                    float(command_args.get(const.KEY_WORD_AMOUNT) or 0),
                )
            case const.CMD_SELL:
                usecases.sell(
                    user,
                    command_args.get(const.KEY_WORD_CURRENCY),
                    float(command_args.get(const.KEY_WORD_AMOUNT) or 0),
                )
            case const.CMD_EXIT:
                is_active = usecases.exit()
                continue
            case _:
                print(f"Неизвестная команда {command}")
                continue

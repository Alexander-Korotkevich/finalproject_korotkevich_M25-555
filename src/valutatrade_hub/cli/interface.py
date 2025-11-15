import prompt  # type: ignore
import shlex

import src.valutatrade_hub.const as const
import src.valutatrade_hub.core.usecases as usecases
import src.valutatrade_hub.core.utils as utils


def run():
    is_active = True

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
            case const.CMD_EXIT:
                is_active = usecases.exit()
                continue
            case _:
                print(f"Неизвестная команда {command}")
                continue

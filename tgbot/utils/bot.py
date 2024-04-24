from aiogram import Bot
from aiogram.types import BotCommand

from tgbot.constants.commands import UserCommands


def get_bot_commands() -> list[BotCommand]:
    bot_commands: list[BotCommand] = []
    for command, description in UserCommands.__members__.items():
        bot_commands.append(
            BotCommand(command, description.value)
        )
    return bot_commands


async def install_bot_commands(bot: Bot):
    await bot.set_my_commands(get_bot_commands())

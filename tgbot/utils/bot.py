from enum import EnumType

from aiogram import Bot
from aiogram.types import BotCommand, User

from tgbot.constants.commands import UserCommands


def get_bot_commands(commands: EnumType = UserCommands) -> list[BotCommand]:
    bot_commands: list[BotCommand] = []
    for command, description in commands.__members__.items():
        bot_commands.append(
            BotCommand(command, description.value)
        )
    return bot_commands


async def install_bot_commands(bot: Bot):
    await bot.set_my_commands(get_bot_commands())


def make_deep_link(bot_info: User, start_data: str) -> str:
    return f'https://t.me/{bot_info.username}?start={start_data}'


def make_start_training_deep_link(bot_info: User, training_data: str):
    return make_deep_link(bot_info, f'train__{training_data}')

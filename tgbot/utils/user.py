from aiogram import Bot
from aiogram.types import ReplyKeyboardMarkup

from tgbot.constants.commands import TrainerCommands, TraineeCommands
from tgbot.keyboards.reply import (
    TRAINER_COMMANDS_KEYBOARD, TRAINEE_COMMANDS_KEYBOARD
)
from tgbot.models.user import User, UserRoles
from tgbot.utils.bot import get_bot_commands


def define_user_keyboard(user: User) -> ReplyKeyboardMarkup:
    if user.role == UserRoles.trainer:
        return TRAINER_COMMANDS_KEYBOARD
    return TRAINEE_COMMANDS_KEYBOARD


async def define_user_commands(user: User, bot: Bot):
    if user.role == UserRoles.trainer:
        await bot.set_my_commands(get_bot_commands(TrainerCommands))
    else:
        await bot.set_my_commands(get_bot_commands(TraineeCommands))

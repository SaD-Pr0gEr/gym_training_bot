from aiogram.types import ReplyKeyboardMarkup

from tgbot.keyboards.reply import TRAINER_COMMANDS_KEYBOARD
from tgbot.models.user import User, UserRoles


def define_user_keyboard(user: User) -> ReplyKeyboardMarkup:
    if user.role == UserRoles.trainer:
        return TRAINER_COMMANDS_KEYBOARD
    return ReplyKeyboardMarkup([])

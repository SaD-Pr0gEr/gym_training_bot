from aiogram.types import KeyboardButton

from tgbot.constants.commands import UserButtonCommands

REGISTER_BUTTON = KeyboardButton(
    UserButtonCommands.register.value, request_contact=True
)

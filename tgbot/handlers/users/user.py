from aiogram import Dispatcher
from aiogram.types import Message

from tgbot.constants.commands import UserCommands


async def user_start(message: Message):
    await message.reply('Hello, user!')


def register_user(dp: Dispatcher):
    dp.register_message_handler(
        user_start, commands=[UserCommands.start.name], state='*'
    )

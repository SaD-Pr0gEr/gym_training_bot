from aiogram import Dispatcher
from aiogram.types import Message

from tgbot.constants.commands import UserCommands


async def admin_start(message: Message):
    await message.reply('Hello, admin!')


def register_admin(dp: Dispatcher):
    dp.register_message_handler(
        admin_start, commands=[UserCommands.start.name], state='*',
        is_admin=True
    )

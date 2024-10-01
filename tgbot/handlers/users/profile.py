from aiogram import Dispatcher
from aiogram.types import Message

from tgbot.constants.commands import UserButtonCommands
from tgbot.models.user import User


async def my_profile_command(message: Message):
    session_class = message.bot['session']
    async with session_class() as session:
        user: User = await User.select(
            session, {'tg_id': message.from_user.id}, True
        )
    await message.answer(user.display_text())


def register_profile_handlers(dp: Dispatcher):
    dp.register_message_handler(
        my_profile_command, text=UserButtonCommands.profile.value,
        logged_user=True
    )

import typing

from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from tgbot.models.user import User, UserRoles


class LoggedUserFilter(BoundFilter):
    key = 'logged_user'

    def __init__(self, logged_user: typing.Optional[bool] = None):
        self.logged_user = logged_user

    async def check(self, obj: Message | CallbackQuery):
        if self.logged_user is None:
            return False
        session_class: async_sessionmaker[AsyncSession] = obj.bot['session']
        async with session_class() as session:
            user: User | None = await User.select(
                session, {'tg_id': obj.from_user.id}, True
            )
        return bool(user) == self.logged_user

import typing

from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from tgbot.models.user import User, UserRoles


class TraineeFilter(BoundFilter):
    key = 'is_trainee'

    def __init__(self, is_trainee: typing.Optional[bool] = None):
        self.is_trainee = is_trainee

    async def check(self, obj: Message | CallbackQuery):
        if self.is_trainee is None:
            return False
        session_class: async_sessionmaker[AsyncSession] = obj.bot['session']
        async with session_class() as session:
            user: User | None = await User.select(
                session, {'tg_id': obj.from_user.id}, True
            )
        if not user:
            return False
        return (user.role.value == UserRoles.trainee.value) == self.is_trainee

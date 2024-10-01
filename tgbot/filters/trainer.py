import typing

from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from tgbot.models.user import User, UserRoles


class TrainerFilter(BoundFilter):
    key = 'is_trainer'

    def __init__(self, is_trainer: typing.Optional[bool] = None):
        self.is_trainer = is_trainer

    async def check(self, obj: Message | CallbackQuery):
        if self.is_trainer is None:
            return False
        session_class: async_sessionmaker[AsyncSession] = obj.bot['session']
        async with session_class() as session:
            user: User | None = await User.select(
                session, {'tg_id': obj.from_user.id}, True
            )
        if not user:
            return False
        return (user.role.value == UserRoles.trainer.value) == self.is_trainer

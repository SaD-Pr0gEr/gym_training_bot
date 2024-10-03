from datetime import datetime

from sqlalchemy import ForeignKey, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tgbot.models.base import Model, BaseModelMixin
from tgbot.models.subscribe import TrainingSubscription
from tgbot.models.training import TrainingTypesDisplay


class TrainingSession(Model, BaseModelMixin):

    __tablename__ = 'training_sessions'

    id: Mapped[int] = mapped_column(primary_key=True)
    subscription_id: Mapped[int] = mapped_column(ForeignKey(
        'training_subscriptions.id'
    ))
    visit_date: Mapped[datetime] = mapped_column(default=datetime.now)

    subscription: Mapped["TrainingSubscription"] = relationship(lazy='joined')

    def __init__(self, subscription_id: int):
        self.subscription_id = subscription_id
        super().__init__()

    @classmethod
    async def select(
            cls, session: AsyncSession, filter_data: dict | None = None,
            in_filters: dict | None = None,
            one: bool = False
    ):
        query = select(cls)
        if filter_data:
            for key, value in filter_data.items():
                query = query.where(getattr(cls, key) == value)
        if in_filters:
            for key, value in in_filters.items():
                query = query.where(getattr(cls, key).in_(value))
        result = await session.execute(query)
        if one:
            return result.scalars().first()
        return result.scalars().all()

    def display_text(self) -> str:
        type_text = getattr(
            TrainingTypesDisplay, self.subscription.plan.type.name
        ).value
        return (
            f'{type_text}({self.subscription.plan.trainer.full_name})\n'
            f'Дата посещения: {self.visit_date.strftime("%d.%m.%Y %H:%M")}'
        )

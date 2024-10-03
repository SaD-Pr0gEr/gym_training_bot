from datetime import datetime

from asyncpg.pgproto.pgproto import timedelta
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tgbot.models.base import Model, BaseModelMixin
from tgbot.models.training import TrainingPlan, TrainingTypesDisplay
from tgbot.models.user import User


class TrainingSubscription(Model, BaseModelMixin):

    __tablename__ = 'training_subscriptions'

    id: Mapped[int] = mapped_column(primary_key=True)
    subscriber_id: Mapped[int] = mapped_column(ForeignKey('users.tg_id'))
    plan_id: Mapped[int] = mapped_column(ForeignKey('training_plans.id'))
    buy_date: Mapped[datetime]
    balance: Mapped[int]

    subscriber: Mapped["User"] = relationship(lazy='joined')
    plan: Mapped["TrainingPlan"] = relationship(lazy='joined')

    def __init__(
            self, subscriber_id: int, plan_id: int, buy_date: datetime,
            balance: int
    ):
        self.subscriber_id = subscriber_id
        self.plan_id = plan_id
        self.buy_date = buy_date
        self.balance = balance
        super().__init__()

    def display_text(self) -> str:
        plan_type = getattr(TrainingTypesDisplay, self.plan.type.name).value
        return (
            f'Тип тренировки: {plan_type}\n'
            f'Остаток: {self.balance}\n'
            f'Дата покупки: {self.buy_date.strftime("%d.%m.%Y %H:%M")}\n'
            f'Действует до: {self.end_date.strftime("%d.%m.%Y %H:%M")}\n'
            f'Просрочен: {"Да" if self.expired else "Нет"}\n'
            f'Тренер: {self.plan.trainer.full_name}'
            f'({self.plan.trainer.phone_number})'
        )

    def inline_btn_text(self) -> str:
        plan_type = getattr(TrainingTypesDisplay, self.plan.type.name).value
        return (
            f'{plan_type}({self.plan.trainer.full_name}) - {self.balance} шт.'
        )

    @property
    def end_date(self) -> datetime:
        return self.buy_date + timedelta(days=31)

    @property
    def expired(self) -> bool:
        return datetime.now() > self.end_date

    @property
    def active(self) -> bool:
        return not self.expired and self.balance

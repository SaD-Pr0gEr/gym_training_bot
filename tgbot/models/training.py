from enum import Enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tgbot.models.base import Model, BaseModelMixin
from tgbot.models.user import User


class TrainingTypes(Enum):
    one_time_personal = 'one_time_personal'
    one_time_split = 'one_time_split'
    personal_count = 'one_time_count'
    personal_split = 'personal_split'


class TrainingTypesDisplay(Enum):
    one_time_personal = 'Одноразовая тренировка'
    one_time_split = 'Одноразовый сплит'
    personal_count = 'Персональные тренировки'
    personal_split = 'Персональные сплиты'


class TrainingPlan(Model, BaseModelMixin):

    __tablename__ = 'training_plans'

    id: Mapped[int] = mapped_column(primary_key=True)
    count: Mapped[int]
    type: Mapped[TrainingTypes]
    trainer_id: Mapped[int] = mapped_column(ForeignKey('users.tg_id'))

    trainer: Mapped["User"] = relationship(lazy='joined')

    def __init__(self, count: int, type_: TrainingTypes, trainer_id: int):
        self.count = count
        self.type = type_
        self.trainer_id = trainer_id
        super().__init__()

    def display_text(self) -> str:
        return (
            f'<b>{getattr(TrainingTypesDisplay, self.type.name).value}</b>\n'
            f'Кол-во тренеровок: {self.count}'
        )

    def inline_btn_text(self) -> str:
        return (
            f'{getattr(TrainingTypesDisplay, self.type.name).value}'
            f'({self.count} шт.)'
        )

    def __str__(self):
        return f'{self.trainer_id}: {self.type}'

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'

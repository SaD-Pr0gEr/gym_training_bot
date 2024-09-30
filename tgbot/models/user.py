from enum import Enum
from sqlalchemy.orm import Mapped, mapped_column

from .base import Model, BaseModelMixin


class UserRoles(Enum):
    trainee = 'trainee'
    trainer = 'trainer'


class UserRolesDisplay(Enum):
    trainee = 'Тренерующийся'
    trainer = 'Тренер'


class User(Model, BaseModelMixin):

    __tablename__ = 'users'

    tg_id: Mapped[int] = mapped_column(primary_key=True)
    phone_number: Mapped[str]
    role: Mapped[UserRoles]

    def __init__(self, tg_id: int, phone_number: str, role: UserRoles):
        self.tg_id = tg_id
        self.phone_number = phone_number
        self.role = role
        super().__init__()

    def __str__(self):
        return f'{self.tg_id}'

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.tg_id}>'

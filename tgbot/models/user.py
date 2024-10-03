from datetime import datetime
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
    full_name: Mapped[str] = mapped_column(default='', server_default='')
    phone_number: Mapped[str]
    role: Mapped[UserRoles]
    register_date: Mapped[datetime] = mapped_column(default=datetime.now())

    def __init__(
        self, tg_id: int, full_name: str, phone_number: str, role: UserRoles
    ):
        self.tg_id = tg_id
        self.full_name = full_name
        self.phone_number = phone_number
        self.role = role
        super().__init__()

    def display_text(self) -> str:
        return (
            f'<b>Ваш профиль 👤</b>\n'
            f'ID: {self.tg_id}\n'
            f'Ф.И.О: {self.full_name}\n'
            f'Номер телефона: {self.phone_number}\n'
            f'Роль: {getattr(UserRolesDisplay, self.role.value).value}\n'
            f'Дата регистрации: {self.register_date}'
        )

    def __str__(self):
        return f'{self.tg_id}'

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.tg_id}>'

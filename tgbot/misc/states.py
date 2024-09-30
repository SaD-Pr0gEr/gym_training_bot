from aiogram.dispatcher.filters.state import State, StatesGroup


class UserRegisterState(StatesGroup):
    phone_number = State()
    role = State()

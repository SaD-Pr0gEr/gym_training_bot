from aiogram.dispatcher.filters.state import State, StatesGroup


class UserRegisterState(StatesGroup):
    phone_number = State()
    full_name = State()
    role = State()


class AddTrainingPlanState(StatesGroup):
    type = State()
    count = State()

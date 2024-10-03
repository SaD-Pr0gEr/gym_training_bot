from enum import Enum


class UserCommands(Enum):
    start = 'Старт бота'


class UserButtonCommands(Enum):
    register = 'Зарегистрироваться 👤'
    profile = 'Профиль 👤'
    settings = 'Изменить профиль ⚙️'


class TrainerButtonCommands(Enum):
    add_plan = 'Добавить план тренировки 🤼'
    plans_list = 'Мои планы тренировок 📋'


class TraineeButtonCommands(Enum):
    buy_plan = 'Купить тренировку 💳'
    my_subscribes = 'Мои тренировки 🏋️‍♂️'

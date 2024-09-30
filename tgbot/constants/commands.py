from enum import Enum


class UserCommands(Enum):
    start = 'Старт бота'


class UserButtonCommands(Enum):
    register = 'Зарегистрироваться 👤'


class TrainerButtonCommands(Enum):
    add_plan = 'Добавить план тренировки 🤼'
    plans_list = 'Мои планы тренировок 📋'

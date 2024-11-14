from enum import Enum


class UserCommands(Enum):
    start = 'Старт бота'
    buy = 'Списать тренировку'


class UserButtonCommands(Enum):
    register = 'Зарегистрироваться 👤'
    profile = 'Мой профиль'
    settings = 'Изменить профиль ⚙️'


class TrainerButtonCommands(Enum):
    add_plan = 'Добавить услугу'
    plans_list = 'Мои услуги'
    remove_training_manual = 'Списание тренировки вручную'
    my_subscribers = 'Список клиентов'


class TraineeButtonCommands(Enum):
    buy_plan = 'Списать тренировку 💳'
    my_subscribes = 'Мои тренировки 🏋️‍♂️'
    start_training = 'Начать тренировку 🏋️‍♂️'
    history = 'История тренировок 📜'

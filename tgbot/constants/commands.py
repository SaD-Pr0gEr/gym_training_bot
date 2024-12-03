from enum import Enum


class UserCommands(Enum):
    start = 'Меню'


class TrainerCommands(Enum):
    start = 'Меню'
    remove = 'Списать тренировку'


class TraineeCommands(Enum):
    start = 'Меню'
    train = 'Начать тренировку'


class UserButtonCommands(Enum):
    register = 'Зарегистрироваться 👤'
    profile = 'Мой профиль'
    settings = 'Изменить ⚙️'
    menu = 'Меню'


class TrainerButtonCommands(Enum):
    add_plan = 'Добавить услугу'
    plans_list = 'Мои услуги'
    remove_training_manual = 'Списание тренировки вручную'
    my_subscribers = 'Список клиентов'
    add_training_count = 'Зачислить тренировку подписчику'


class TraineeButtonCommands(Enum):
    buy_plan = 'Купить тренировку 💳'
    my_subscribes = 'Мои тренировки 🏋️‍♂️'
    start_training = 'Начать тренировку 🏋️‍♂️'
    history = 'История тренировок 📜'

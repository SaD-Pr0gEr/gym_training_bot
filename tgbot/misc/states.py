from aiogram.dispatcher.filters.state import State, StatesGroup


class UserRegisterState(StatesGroup):
    phone_number = State()
    full_name = State()
    role = State()


class AddTrainingPlanState(StatesGroup):
    type = State()
    count = State()


class UserSettingsSetState(StatesGroup):
    choose_field = State()
    set_full_name = State()
    set_role = State()


class SubscribeUserState(StatesGroup):
    search_trainer = State()
    choose_trainer = State()
    choose_plan = State()


class StartTrainState(StatesGroup):
    choose_plan = State()


class RemoveTrainingSessionManualState(StatesGroup):
    choose_plan = State()
    choose_user = State()


class AddTrainingSessionCountState(StatesGroup):
    choose_user = State()
    choose_plan = State()
    add_count = State()


class ShowTrainerSubsState(StatesGroup):
    choose_user = State()

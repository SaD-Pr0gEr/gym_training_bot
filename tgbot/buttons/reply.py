from aiogram.types import KeyboardButton

from tgbot.constants.commands import UserButtonCommands, TrainerButtonCommands, \
    TraineeButtonCommands

REGISTER_BUTTON = KeyboardButton(
    UserButtonCommands.register.value, request_contact=True
)
ADD_PLAN_BUTTON = KeyboardButton(TrainerButtonCommands.add_plan.value)
PLANS_LIST_BUTTON = KeyboardButton(TrainerButtonCommands.plans_list.value)
USER_PROFILE_BUTTON = KeyboardButton(UserButtonCommands.profile.value)
USER_SETTINGS_BUTTON = KeyboardButton(UserButtonCommands.settings.value)
BUY_PLAN_BUTTON = KeyboardButton(TraineeButtonCommands.buy_plan.value)
MY_SUBS_BUTTON = KeyboardButton(TraineeButtonCommands.my_subscribes.value)
START_TRAINING_BUTTON = KeyboardButton(
    TraineeButtonCommands.start_training.value
)
HISTORY_COMMAND = KeyboardButton(TraineeButtonCommands.history.value)

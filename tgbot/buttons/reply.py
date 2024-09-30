from aiogram.types import KeyboardButton

from tgbot.constants.commands import UserButtonCommands, TrainerButtonCommands

REGISTER_BUTTON = KeyboardButton(
    UserButtonCommands.register.value, request_contact=True
)
ADD_PLAN_BUTTON = KeyboardButton(TrainerButtonCommands.add_plan.value)
PLANS_LIST_BUTTON = KeyboardButton(TrainerButtonCommands.plans_list.value)

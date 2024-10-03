from aiogram import Dispatcher

from .plan import register_trainer_plans_handlers
from .subscribe import register_trainer_subscribe_handlers


def register_trainers_handlers(dp: Dispatcher):
    register_trainer_plans_handlers(dp)
    register_trainer_subscribe_handlers(dp)

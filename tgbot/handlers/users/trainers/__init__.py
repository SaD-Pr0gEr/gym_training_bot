from aiogram import Dispatcher

from .plan import register_trainer_plans_handlers


def register_trainers_handlers(dp: Dispatcher):
    register_trainer_plans_handlers(dp)

from aiogram import Dispatcher

from .trainers import register_trainers_handlers
from .user import register_user


def register_all_user_handlers(dp: Dispatcher):
    register_user(dp)
    register_trainers_handlers(dp)

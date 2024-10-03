from aiogram import Dispatcher

from .profile import register_profile_handlers
from .settings import register_settings_handlers
from .trainees import register_trainees_handlers
from .trainers import register_trainers_handlers
from .user import register_user


def register_all_user_handlers(dp: Dispatcher):
    register_user(dp)
    register_trainers_handlers(dp)
    register_profile_handlers(dp)
    register_settings_handlers(dp)
    register_trainees_handlers(dp)

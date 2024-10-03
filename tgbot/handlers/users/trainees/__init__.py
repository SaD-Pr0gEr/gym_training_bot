from aiogram import Dispatcher

from .sessions import register_sessions_handlers
from .subscribe import register_subscribes_handlers


def register_trainees_handlers(dp: Dispatcher):
    register_subscribes_handlers(dp)
    register_sessions_handlers(dp)

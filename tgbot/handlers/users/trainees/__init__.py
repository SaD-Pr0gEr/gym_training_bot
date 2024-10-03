from aiogram import Dispatcher

from .subscribe import register_subscribes_handlers


def register_trainees_handlers(dp: Dispatcher):
    register_subscribes_handlers(dp)

import tgbot.buttons.reply as r_btn
from aiogram.types import ReplyKeyboardMarkup

USER_REGISTER_KEYBOARD = ReplyKeyboardMarkup([[
    r_btn.REGISTER_BUTTON
]], resize_keyboard=True)

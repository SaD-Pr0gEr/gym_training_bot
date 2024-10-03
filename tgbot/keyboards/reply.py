import tgbot.buttons.reply as r_btn
from aiogram.types import ReplyKeyboardMarkup

USER_REGISTER_KEYBOARD = ReplyKeyboardMarkup([[
    r_btn.REGISTER_BUTTON
]], resize_keyboard=True)

TRAINER_COMMANDS_KEYBOARD = ReplyKeyboardMarkup([
    [r_btn.ADD_PLAN_BUTTON, r_btn.PLANS_LIST_BUTTON],
    [r_btn.USER_PROFILE_BUTTON, r_btn.USER_SETTINGS_BUTTON]
], resize_keyboard=True)

TRAINEE_COMMANDS_KEYBOARD = ReplyKeyboardMarkup([
    [r_btn.USER_PROFILE_BUTTON, r_btn.USER_SETTINGS_BUTTON],
    [r_btn.BUY_PLAN_BUTTON, r_btn.MY_SUBS_BUTTON]
], resize_keyboard=True)

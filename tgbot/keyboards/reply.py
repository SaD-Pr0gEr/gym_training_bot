import tgbot.buttons.reply as r_btn
from aiogram.types import ReplyKeyboardMarkup

USER_REGISTER_KEYBOARD = ReplyKeyboardMarkup([[
    r_btn.REGISTER_BUTTON
]], resize_keyboard=True)

TRAINER_COMMANDS_KEYBOARD = ReplyKeyboardMarkup([
    [r_btn.PLANS_LIST_BUTTON],
    [r_btn.USER_PROFILE_BUTTON, r_btn.MY_SUBSCRIBERS_BUTTON],
], resize_keyboard=True)

TRAINEE_COMMANDS_KEYBOARD = ReplyKeyboardMarkup([
    [r_btn.USER_PROFILE_BUTTON, r_btn.START_TRAINING_BUTTON],
    [r_btn.BUY_PLAN_BUTTON, r_btn.MY_SUBS_BUTTON],
], resize_keyboard=True)

TRAINER_SERVICES_KEYBOARD = ReplyKeyboardMarkup([
    [r_btn.ADD_PLAN_BUTTON, r_btn.MAIN_MENU_BUTTON],
], resize_keyboard=True)

TRAINER_SUBSCRIBERS_KEYBOARD = ReplyKeyboardMarkup([
    [r_btn.ADD_SESSION_COUNT, r_btn.REMOVE_PLAN_BUTTON],
    [r_btn.MAIN_MENU_BUTTON],
], resize_keyboard=True)

USER_SETTINGS_KEYBOARD = ReplyKeyboardMarkup([
    [r_btn.USER_SETTINGS_BUTTON, r_btn.MAIN_MENU_BUTTON],
], resize_keyboard=True)

USER_SUBS_KEYBOARD = ReplyKeyboardMarkup([
    [r_btn.HISTORY_COMMAND, r_btn.MAIN_MENU_BUTTON],
], resize_keyboard=True)

from enum import EnumType

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import tgbot.buttons.inline as inline_btns
from tgbot.misc.enum import two_enums_get_by_key


USER_SETTINGS_INLINE_KEYBOARD = InlineKeyboardMarkup(inline_keyboard=[
    [inline_btns.FULL_NAME_CHANGE_BTN],
    [inline_btns.ROLE_CHANGE_BTN],
])


def two_enums_value_inline_keyboard(
        enum1: EnumType, enum2: EnumType
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    for enum_ in two_enums_get_by_key(enum1, enum2):
        keyboard.add(InlineKeyboardButton(
            enum_.value, callback_data=enum_.name
        ))
    return keyboard

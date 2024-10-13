from enum import EnumType
from typing import Iterable

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import tgbot.buttons.inline as inline_btns
from tgbot.misc.enum import two_enums_get_by_key
from tgbot.models.subscribe import TrainingSubscription
from tgbot.models.training import TrainingPlan

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


def make_inline_kb_from_objects_list(
        obj_list: list[object], display_attr_name: str, callback_attr_name: str
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    for obj in obj_list:
        btn = inline_btns.make_inline_btn_from_obj(
            obj, display_attr_name, callback_attr_name
        )
        keyboard.add(btn)
    return keyboard


def make_inline_kb_plans(plans: list[TrainingPlan]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    for plan in plans:
        txt = plan.inline_btn_text()
        keyboard.add(InlineKeyboardButton(txt, callback_data=str(plan.id)))
    return keyboard


def make_inline_kb_user_from_subscribes(
    subs: Iterable[TrainingSubscription]
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    for sub in subs:
        keyboard.add(InlineKeyboardButton(
            f'{sub.subscriber.full_name}({sub.subscriber.phone_number})',
            callback_data=str(sub.subscriber_id)
        ))
    return keyboard

from typing import Any

from aiogram.types import InlineKeyboardButton

FULL_NAME_CHANGE_BTN = InlineKeyboardButton('Ф.И.О', callback_data='full_name')
ROLE_CHANGE_BTN = InlineKeyboardButton('Роль в зале', callback_data='role')


def make_inline_btn_from_obj(
        obj: object, display_attr_name: str, callback_data_attr_name: str
) -> InlineKeyboardButton:
    attr = getattr(obj, display_attr_name)
    return InlineKeyboardButton(
        str(attr if not callable(attr) else attr()),
        callback_data=str(getattr(obj, callback_data_attr_name))
    )


def make_yes_inline_btn(callback_data: str = '') -> InlineKeyboardButton:
    return InlineKeyboardButton('Да ✅', callback_data=f'yes__{callback_data}')


def make_cancel_inline_btn(callback_data: str = '') -> InlineKeyboardButton:
    return InlineKeyboardButton(
        'Отменить ❌', callback_data=f'cancel__{callback_data}'
    )


def make_no_inline_btn(callback_data: str = '') -> InlineKeyboardButton:
    return InlineKeyboardButton('Нет ❌', callback_data=f'no__{callback_data}')


def make_search_inline_btn(callback_data: str = '') -> InlineKeyboardButton:
    return InlineKeyboardButton(
        'Поиск 🔍', callback_data=f'search__{callback_data}'
    )

def make_prev_month_inline_btn(
        callback_data: Any = ''
) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        '<< Предыдущий месяц', callback_data=f'prev_month__{callback_data}'
    )

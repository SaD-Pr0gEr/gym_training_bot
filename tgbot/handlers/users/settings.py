from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from tgbot.constants.commands import UserButtonCommands
from tgbot.keyboards.inline import (
    USER_SETTINGS_INLINE_KEYBOARD, two_enums_value_inline_keyboard
)
from tgbot.misc.states import UserSettingsSetState
from tgbot.models.user import UserRoles, UserRolesDisplay, User
from tgbot.utils.user import define_user_keyboard


async def profile_settings_command(message: Message):
    await UserSettingsSetState.choose_field.set()
    await message.answer(
        'Отлично! Выберите что поменять',
        reply_markup=USER_SETTINGS_INLINE_KEYBOARD
    )


async def set_settings_callback(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'full_name':
        await state.update_data(choose_field='full_name')
        await UserSettingsSetState.set_full_name.set()
        await callback.bot.send_message(
            callback.from_user.id,
            'Введите новое Ф.И.О'
        )
    else:
        await state.update_data(choose_field='role')
        await UserSettingsSetState.set_role.set()
        await callback.bot.send_message(
            callback.from_user.id,
            'Выберите новую роль',
            reply_markup=two_enums_value_inline_keyboard(
                UserRoles, UserRolesDisplay
            )
        )
    await callback.bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )


async def set_role_callback(callback: CallbackQuery, state: FSMContext):
    session_class: async_sessionmaker[AsyncSession] = callback.bot['session']
    async with state.proxy() as data:
        field_name = data['choose_field']
    await state.finish()
    async with session_class() as session:
        await User.update(
            session, {'tg_id': callback.from_user.id},
            {field_name: UserRoles(callback.data)}
        )
        await session.commit()
        user = await User.select(
            session, {'tg_id': callback.from_user.id}, True
        )
    await callback.bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )
    await callback.bot.send_message(
        callback.from_user.id,
        'Успешно обновил профиль',
        reply_markup=define_user_keyboard(user)
    )


async def set_full_name(message: Message, state: FSMContext):
    session_class: async_sessionmaker[AsyncSession] = message.bot['session']
    async with state.proxy() as data:
        field_name = data['choose_field']
    await state.finish()
    async with session_class() as session:
        await User.update(
            session, {'tg_id': message.from_user.id},
            {field_name: message.text}
        )
        await session.commit()
        user = await User.select(
            session, {'tg_id': message.from_user.id}, True
        )
    await message.answer(
        'Успешно обновил профиль',
        reply_markup=define_user_keyboard(user)
    )


async def main_menu_command(message: Message):
    session_class: async_sessionmaker[AsyncSession] = message.bot['session']
    async with session_class() as session:
        user = await User.select(
            session, {'tg_id': message.from_user.id}, True
        )
    await message.answer(
        'Отлично! Выберите команду', reply_markup=define_user_keyboard(user)
    )


def register_settings_handlers(dp: Dispatcher):
    dp.register_message_handler(
        profile_settings_command, text=UserButtonCommands.settings.value,
        logged_user=True
    )
    dp.register_message_handler(
        main_menu_command, text=UserButtonCommands.menu.value,
        logged_user=True
    )
    dp.register_callback_query_handler(
        set_settings_callback, state=UserSettingsSetState.choose_field
    )
    dp.register_callback_query_handler(
        set_role_callback, state=UserSettingsSetState.set_role
    )
    dp.register_message_handler(
        set_full_name, state=UserSettingsSetState.set_full_name
    )

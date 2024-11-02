from aiogram import Dispatcher
from aiogram.types import Message, ContentType, CallbackQuery
from aiogram.dispatcher import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from tgbot.constants.commands import UserCommands
from tgbot.keyboards.inline import two_enums_value_inline_keyboard
from tgbot.keyboards.reply import USER_REGISTER_KEYBOARD
from tgbot.misc.states import UserRegisterState
from tgbot.models.sessions import TrainingSession
from tgbot.models.subscribe import TrainingSubscription
from tgbot.models.user import User, UserRoles, UserRolesDisplay
from tgbot.utils.user import define_user_keyboard


async def user_start(message: Message, state: FSMContext):
    await state.finish()
    session_class: async_sessionmaker[AsyncSession] = message.bot['session']
    async with session_class() as session:
        user: User | None = await User.select(
            session, {'tg_id': message.from_user.id}, True
        )
    if not user:
        await UserRegisterState.phone_number.set()
        await message.answer(
            'Вы не зарегистрированы, чтобы зарегистрироваться нажмите кнопку '
            'зарегистрироваться', reply_markup=USER_REGISTER_KEYBOARD
        )
    else:
        display = getattr(UserRolesDisplay, user.role.value)
        await message.answer(
            f'Приветствую, {display.value}! Выбери команду',
            reply_markup=define_user_keyboard(user)
        )


async def get_user_number(message: Message, state: FSMContext):
    await state.update_data(phone_number=message.contact.phone_number)
    await UserRegisterState.full_name.set()
    await message.answer('Отлично! Напишите свое ФИО')


async def get_user_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await UserRegisterState.role.set()
    await message.answer(
        'Отлично! Выберите свою роль',
        reply_markup=two_enums_value_inline_keyboard(
            UserRoles, UserRolesDisplay
        )
    )


async def get_user_role(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        number = data['phone_number']
        full_name = data['full_name']
    await state.finish()
    role = UserRoles(callback.data)
    session_class: async_sessionmaker[AsyncSession] = callback.bot['session']
    async with session_class() as session:
        user = User(callback.from_user.id, full_name, number, role)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    await callback.bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )
    await callback.bot.send_message(
        callback.from_user.id,
        'Вы успешно зарегистрировались',
        reply_markup=define_user_keyboard(user)
    )


def register_user(dp: Dispatcher):
    dp.register_message_handler(
        user_start, commands=[UserCommands.start.name], state='*'
    )
    dp.register_message_handler(
        get_user_number, state=UserRegisterState.phone_number,
        content_types=[ContentType.CONTACT]
    )
    dp.register_message_handler(
        get_user_full_name, state=UserRegisterState.full_name,
    )
    dp.register_callback_query_handler(
        get_user_role, state=UserRegisterState.role
    )

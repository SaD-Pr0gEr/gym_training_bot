from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
)
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from tgbot.buttons.inline import (
    make_yes_inline_btn, make_no_inline_btn, make_search_inline_btn
)
from tgbot.constants.commands import TraineeButtonCommands, UserCommands
from tgbot.keyboards.inline import (
    make_inline_kb_plans, make_inline_kb_from_objects_list
)
from tgbot.keyboards.reply import USER_SUBS_KEYBOARD
from tgbot.misc.states import SubscribeUserState
from tgbot.models.subscribe import TrainingSubscription
from tgbot.models.training import TrainingPlan
from tgbot.models.user import User, UserRoles


async def subscribe_to_plan_command(message: Message):
    session_class: async_sessionmaker[AsyncSession] = message.bot['session']
    async with session_class() as session:
        trainers = await User.select(session, {'role': UserRoles.trainer})
    if not trainers:
        await message.answer('Подходящих тренеров нет')
        return
    await SubscribeUserState.search_trainer.set()
    async with session_class() as session:
        user_plans_ids = (
            await session.execute(
                select(TrainingSubscription.plan_id)
                .where(
                    TrainingSubscription.subscriber_id == message.from_user.id
                )
                .distinct(TrainingSubscription.plan_id)
            )
        ).scalars().all()
        user_trainers = (
            await session.execute(
                select(TrainingPlan)
                .where(TrainingPlan.id.in_(user_plans_ids))
                .distinct(TrainingPlan.trainer_id)
            )
        ).scalars().all()
    keyboard = InlineKeyboardMarkup()
    keyboard.add(make_search_inline_btn('trainer'))
    for plan in user_trainers:
        keyboard.add(InlineKeyboardButton(
            plan.trainer.full_name,
            callback_data=f'{plan.trainer_id}'
        ))
    await message.answer(
        'Отлично! Выберите 1го из своих тренеров или поищите другого',
        reply_markup=keyboard
    )


async def choose_trainer_callback(callback: CallbackQuery, state: FSMContext):
    await callback.bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )
    if callback.data == 'search__trainer':
        await SubscribeUserState.choose_trainer.set()
        await callback.bot.send_message(
            callback.from_user.id,
            'Отлично! Напишите имя тренера для поиска'
        )
    else:
        trainer_id = int(callback.data)
        session_class: async_sessionmaker[AsyncSession] = (
            callback.bot['session']
        )
        async with session_class() as session:
            plans = await TrainingPlan.select(
                session, {'trainer_id': trainer_id}
            )
        if not plans:
            await callback.bot.send_message(
                callback.from_user.id,
                'У этого тренера нет подходящих тарифов'
            )
            await state.finish()
            return
        await SubscribeUserState.choose_plan.set()
        keyboard = make_inline_kb_plans(plans)
        await callback.bot.send_message(
            callback.from_user.id,
            'Отлично! Выберите план',
            reply_markup=keyboard
        )


async def search_trainer(message: Message, state: FSMContext):
    session_class: async_sessionmaker[AsyncSession] = message.bot['session']
    async with session_class() as session:
        trainers = (await session.execute(
            select(User)
            .where(User.full_name.icontains(message.text))
        )).scalars().all()
    if not trainers:
        await message.answer(
            'Тренеров по запросу нет, команда завершена. Попробуйте заново'
        )
        await state.finish()
        return
    await SubscribeUserState.search_trainer.set()
    keyboard = make_inline_kb_from_objects_list(trainers, 'full_name', 'tg_id')
    keyboard.add(make_search_inline_btn('trainer'))
    await message.answer('Результаты поиска', reply_markup=keyboard)


async def choose_plan_callback(callback: CallbackQuery, state: FSMContext):
    plan_id = int(callback.data)
    session_class: async_sessionmaker[AsyncSession] = callback.bot['session']
    async with session_class() as session:
        plan: TrainingPlan = await TrainingPlan.select(
            session, {'id': plan_id}, True
        )
        current_user: User = await User.select(
            session, {'tg_id': callback.from_user.id}, True
        )
    callback_data = f'plan_{plan_id}__{current_user.tg_id}__{plan.trainer_id}'
    await callback.bot.send_message(
        plan.trainer_id,
        f'К вашему курсу {plan.inline_btn_text()} '
        f'хочет присоединиться пользователь:\n'
        f'{current_user.full_name}({current_user.phone_number})\n'
        f'Принять запрос?',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                make_yes_inline_btn(callback_data),
                make_no_inline_btn(callback_data)
            ]
        ])
    )
    await state.finish()
    await callback.bot.send_message(
        callback.from_user.id,
        'Отправил тренеру запрос, как только он подтвердит вы получите '
        'уведомление и тренировку'
    )
    await callback.bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )


async def subscribes_list_command(message: Message):
    session_class: async_sessionmaker[AsyncSession] = message.bot['session']
    async with session_class() as session:
        user_subs = (
            await session.execute(select(TrainingSubscription).where(and_(
                TrainingSubscription.subscriber_id == message.from_user.id,
                TrainingSubscription.balance > 0
            )))
        ).scalars().all()
    if not user_subs:
        await message.answer('У вас нет купленных тренировок')
    else:
        await message.answer(
            'Ваши тренировки:\n\n' +
            '\n\n'.join(map(lambda obj: obj.display_text(), user_subs)),
            reply_markup=USER_SUBS_KEYBOARD
        )


def register_subscribes_handlers(dp: Dispatcher):
    dp.register_message_handler(
        subscribe_to_plan_command, text=TraineeButtonCommands.buy_plan.value,
        is_trainee=True
    )
    dp.register_callback_query_handler(
        choose_trainer_callback, state=SubscribeUserState.search_trainer
    )
    dp.register_message_handler(
        search_trainer, state=SubscribeUserState.choose_trainer
    )
    dp.register_callback_query_handler(
        choose_plan_callback, state=SubscribeUserState.choose_plan
    )
    dp.register_message_handler(
        subscribes_list_command, text=TraineeButtonCommands.my_subscribes.value
    )

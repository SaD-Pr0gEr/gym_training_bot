from datetime import datetime

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.sql.functions import count

from tgbot.buttons.inline import (
    make_yes_inline_btn, make_no_inline_btn, make_prev_month_inline_btn,
    make_cancel_inline_btn
)
from tgbot.constants.commands import TraineeButtonCommands
from tgbot.keyboards.inline import make_inline_kb_from_objects_list
from tgbot.misc.states import StartTrainState, TraineeSessionsState
from tgbot.models.sessions import TrainingSession
from tgbot.models.subscribe import TrainingSubscription
from tgbot.models.training import TrainingTypesDisplay


async def start_training_command(message: Message):
    session_class: async_sessionmaker[AsyncSession] = message.bot['session']
    async with session_class() as session:
        subs: list[TrainingSubscription] = await TrainingSubscription.select(
            session,
            {'subscriber_id': message.from_user.id}
        )
        subs = [sub for sub in subs if sub.active]
    if not subs:
        await message.answer(
            'У вас нет активных программ(просрочено/0 на балансе)'
        )
        return
    await StartTrainState.choose_plan.set()
    keyboard = make_inline_kb_from_objects_list(subs, 'inline_btn_text', 'id')
    await message.answer('Выберите свою тренировку', reply_markup=keyboard)


async def choose_training_callback(callback: CallbackQuery, state: FSMContext):
    await state.finish()
    sub_id = int(callback.data)
    session = callback.bot['session']
    async with session() as session:
        subscription: TrainingSubscription = await TrainingSubscription.select(
            session, {'id': sub_id}, True
        )
    await callback.bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )
    callback_data = f'session__{subscription.id}'
    await callback.bot.send_message(
        subscription.plan.trainer_id,
        f'Подтвердите списание 1 тренировки\n{subscription.inline_btn_text()}',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                make_yes_inline_btn(callback_data),
                make_no_inline_btn(callback_data)
            ]
        ])
    )
    await callback.bot.send_message(
        callback.from_user.id,
        'Тренеру отправлено уведомление, как только он подтвердит, тренировка '
        'будет списана'
    )


async def sessions_list(message: Message):
    session_class: async_sessionmaker[AsyncSession] = message.bot['session']
    now = datetime.now()
    start_month = datetime(now.year, now.month, 1)
    if now.month == 1:
        prev_month = datetime(now.year-1, 12, 1)
    else:
        prev_month = datetime(now.year, now.month-1, 1)
    if prev_month.month == 2:
        prev_month_end = datetime(prev_month.year, prev_month.month, 28)
    elif prev_month.month in [4, 6, 9, 11]:
        prev_month_end = datetime(prev_month.year, prev_month.month, 30)
    else:
        prev_month_end = datetime(prev_month.year, prev_month.month, 31)
    async with session_class() as session:
        subs_ids = (
            await session.execute(
                select(TrainingSubscription.id)
                .where(
                    TrainingSubscription.subscriber_id == message.from_user.id
                )
            )
        )
        subs_ids = subs_ids.scalars().all()
        this_month_history = (await session.execute(
            select(TrainingSession)
            .where(and_(
                TrainingSession.visit_date.between(start_month, now),
                TrainingSession.subscription_id.in_(subs_ids)
            ))
        )).scalars().all()
        prev_month_exists_history = (await session.execute(
            select(count())
            .where(and_(
                TrainingSession.visit_date.between(prev_month, prev_month_end),
                TrainingSession.subscription_id.in_(subs_ids)
            ))
        )).scalars().first()
    keyboard = InlineKeyboardMarkup()
    if prev_month_exists_history:
        keyboard.add(make_prev_month_inline_btn(
            f'{prev_month.year}__{prev_month.month}'
        ))
    keyboard.add(make_cancel_inline_btn())
    await TraineeSessionsState.choose_month.set()
    if not this_month_history:
        await message.answer(
            'Вы не посещали тренировки на этом месяце', reply_markup=keyboard
        )
        return
    group_history: dict[int, list[TrainingSession]] = {}
    for history in this_month_history:
        if history.subscription_id not in group_history:
            group_history[history.subscription_id] = []
        group_history[history.subscription_id].append(history)
    text = '<b>История тренировок на этом месяце</b>\n\n'
    for group_id, sessions in group_history.items():
        type_text = getattr(
            TrainingTypesDisplay, sessions[0].subscription.plan.type.name
        ).value
        text += (
            f'{type_text}({sessions[0].subscription.plan.trainer.full_name})\n'
        )
        for session in sessions:
            text += session.display_text() + '\n'
        text += '\n\n'
    await message.answer(text, reply_markup=keyboard)


async def show_prev_month_sessions(callback: CallbackQuery, state: FSMContext):
    btn = make_cancel_inline_btn()
    if btn.callback_data in callback.data:
        await state.finish()
        await callback.bot.send_message(
            callback.from_user.id,
            'Отменил команду'
        )
    else:
        session_class: async_sessionmaker[AsyncSession] = (
            callback.bot['session']
        )
        existing_year, existing_month = list(map(
            int, callback.data.replace('prev_month__', '').split('__')
        ))
        start_month = datetime(existing_year, existing_month, 1)
        if start_month.month == 2:
            end_month = datetime(start_month.year, start_month.month, 28)
        elif start_month.month in [4, 6, 9, 11]:
            end_month = datetime(start_month.year, start_month.month, 30)
        else:
            end_month = datetime(start_month.year, start_month.month, 31)
        if existing_month == 1:
            prev_month = datetime(existing_year - 1, 12, 1)
        else:
            prev_month = datetime(existing_year, existing_month - 1, 1)
        if prev_month.month == 2:
            prev_month_end = datetime(prev_month.year, prev_month.month, 28)
        elif prev_month.month in [4, 6, 9, 11]:
            prev_month_end = datetime(prev_month.year, prev_month.month, 30)
        else:
            prev_month_end = datetime(prev_month.year, prev_month.month, 31)
        async with session_class() as session:
            subs_ids = (
                await session.execute(
                    select(TrainingSubscription.id)
                    .where(
                        TrainingSubscription.subscriber_id == callback.from_user.id
                    )
                )
            )
            subs_ids = subs_ids.scalars().all()
            this_month_history = (await session.execute(
                select(TrainingSession)
                .where(and_(
                    TrainingSession.visit_date.between(start_month, end_month),
                    TrainingSession.subscription_id.in_(subs_ids)
                ))
            )).scalars().all()
            prev_month_exists_history = (await session.execute(
                select(count())
                .where(and_(
                    TrainingSession.visit_date.between(prev_month,
                                                       prev_month_end),
                    TrainingSession.subscription_id.in_(subs_ids)
                ))
            )).scalars().first()
        group_history: dict[int, list[TrainingSession]] = {}
        for history in this_month_history:
            if history.subscription_id not in group_history:
                group_history[history.subscription_id] = []
            group_history[history.subscription_id].append(history)
        text = '<b>История тренировок на этом месяце</b>\n\n'
        for group_id, sessions in group_history.items():
            type_text = getattr(
                TrainingTypesDisplay, sessions[0].subscription.plan.type.name
            ).value
            text += (
                f'{type_text}({sessions[0].subscription.plan.trainer.full_name})\n'
            )
            for session in sessions:
                text += session.display_text() + '\n'
            text += '\n\n'
        keyboard = InlineKeyboardMarkup()
        if prev_month_exists_history:
            keyboard.add(make_prev_month_inline_btn(
                f'{prev_month.year}__{prev_month.month}'
            ))
        keyboard.add(make_cancel_inline_btn())
        await callback.bot.send_message(
            callback.from_user.id, text, reply_markup=keyboard
        )
    await callback.message.delete()


def register_sessions_handlers(dp: Dispatcher):
    dp.register_message_handler(
        start_training_command,
        text=TraineeButtonCommands.start_training.value, is_trainee=True
    )
    dp.register_callback_query_handler(
        choose_training_callback, state=StartTrainState.choose_plan
    )
    dp.register_message_handler(
        sessions_list, text=TraineeButtonCommands.history.value,
        is_trainee=True
    )
    dp.register_callback_query_handler(
        show_prev_month_sessions, state=TraineeSessionsState.choose_month
    )

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from tgbot.constants.commands import TrainerButtonCommands
from tgbot.keyboards.inline import (
    make_inline_kb_from_objects_list,
    make_inline_kb_user_from_subscribes
)
from tgbot.misc.states import RemoveTrainingSessionManualState
from tgbot.models.subscribe import TrainingSubscription
from tgbot.models.training import TrainingPlan
from tgbot.utils.text import divide_sequence_to_parts


async def set_point_manual_command(message: Message):
    session_class: async_sessionmaker[AsyncSession] = message.bot['session']
    async with session_class() as session:
        plans_ids_query = (
            select(TrainingPlan.id)
            .where(TrainingPlan.trainer_id == message.from_user.id)
        )
        plans_ids = (await session.execute(plans_ids_query)).scalars().all()
        if not plans_ids:
            await message.answer('У вас нет подходящих пакетов')
            return
        subscribers_query = (
            select(TrainingSubscription)
            .where(TrainingSubscription.plan_id.in_(plans_ids))
            .distinct(TrainingSubscription.subscriber_id)
        )
        subscribers = (
            await session.execute(subscribers_query)
        ).scalars().all()
        if not subscribers:
            await message.answer(
                'У вас нет тренерующихся'
            )
            return
    await RemoveTrainingSessionManualState.choose_user.set()
    await message.answer(
        'Выберите подписчика',
        reply_markup=make_inline_kb_user_from_subscribes(subscribers)
    )


async def choose_subscriber_callback(callback: CallbackQuery):
    subscriber_id = int(callback.data)
    session_class: async_sessionmaker[AsyncSession] = callback.bot['session']
    async with session_class() as session:
        plans_ids_query = (
            select(TrainingPlan.id)
            .where(TrainingPlan.trainer_id == callback.from_user.id)
        )
        plans_ids = (await session.execute(plans_ids_query)).scalars().all()
        plan_subs_query = (
            select(TrainingSubscription)
            .where(and_(
                TrainingSubscription.plan_id.in_(plans_ids),
                TrainingSubscription.subscriber_id == subscriber_id
            ))
        )
        plan_subs = (await session.execute(plan_subs_query)).scalars().all()
    await RemoveTrainingSessionManualState.choose_plan.set()
    keyboard = make_inline_kb_from_objects_list(
        plan_subs, 'inline_btn_plan_balance_text', 'id'
    )
    await callback.bot.send_message(
        callback.from_user.id,
        'Выберите план',
        reply_markup=keyboard
    )
    await callback.bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )


async def choose_plan_callback(callback: CallbackQuery, state: FSMContext):
    sub_id = int(callback.data)
    session_class: async_sessionmaker[AsyncSession] = callback.bot['session']
    await state.finish()
    async with session_class() as session:
        subs: TrainingSubscription = (
            await TrainingSubscription.select(session, {'id': sub_id}, True)
        )
        if subs.balance:
            await TrainingSubscription.update(
                session, {'id': sub_id}, {'balance': subs.balance - 1}
            )
            await session.commit()
            await session.refresh(subs)
    await callback.bot.send_message(
        callback.from_user.id,
        'Успешно списал 1 занятие'
    )
    await callback.bot.send_message(
        subs.subscriber_id,
        f'С вас тренер списал 1 тренировку вручную\n'
        f'<b>Информация о тренировке</b>\n'
        f'{subs.display_text()}'
    )
    await callback.bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )


async def user_subscribers(message: Message):
    session_class: async_sessionmaker[AsyncSession] = message.bot['session']
    async with session_class() as session:
        query_plan = (
            select(TrainingPlan.id)
            .where(TrainingPlan.trainer_id == message.from_user.id)
        )
        plan_ids = (await session.execute(query_plan)).scalars().all()
        query = (
            select(TrainingSubscription)
            .where(TrainingSubscription.plan_id.in_(plan_ids))
        )
        result = (await session.execute(query)).scalars().all()
    if not result:
        await message.answer('У вас нет подписчиков')
        return
    msg_parts: list[str] = []
    for part in divide_sequence_to_parts(result, 4):
        msg_parts.append('\n\n'.join((
            obj.display_text_buyer() for obj in part
        )))
    msg_parts[0] = f'Покупатели тарифов({len(result)} шт.)\n\n' + msg_parts[0]
    for msg in msg_parts:
        await message.answer(msg)


def register_trainer_subscribe_handlers(dp: Dispatcher):
    dp.register_message_handler(
        set_point_manual_command,
        text=TrainerButtonCommands.remove_training_manual.value,
        is_trainer=True
    )
    dp.register_callback_query_handler(
        choose_subscriber_callback,
        state=RemoveTrainingSessionManualState.choose_user
    )
    dp.register_callback_query_handler(
        choose_plan_callback,
        state=RemoveTrainingSessionManualState.choose_plan
    )
    dp.register_message_handler(
        user_subscribers,
        text=TrainerButtonCommands.my_subscribers.value, is_trainer=True
    )

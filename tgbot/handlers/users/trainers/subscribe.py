from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
)
from sqlalchemy import select, and_, Sequence
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from tgbot.constants.commands import TrainerButtonCommands, UserCommands
from tgbot.keyboards.inline import (
    make_inline_kb_from_objects_list,
    make_inline_kb_user_from_subscribes
)
from tgbot.misc.states import (
    RemoveTrainingSessionManualState,
    AddTrainingSessionCountState, ShowTrainerSubsState
)
from tgbot.models.sessions import TrainingSession
from tgbot.models.subscribe import TrainingSubscription
from tgbot.models.training import TrainingPlan


async def remove_count_manual_command(message: Message):
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
            t_session = TrainingSession(subs.id)
            session.add(t_session)
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
            .distinct(TrainingSubscription.subscriber_id)
        )
        result = (await session.execute(query)).scalars().all()
    if not result:
        await message.answer('У вас нет подписчиков')
        return
    await ShowTrainerSubsState.choose_user.set()
    keyboard = InlineKeyboardMarkup()
    for sub in result:
        keyboard.add(InlineKeyboardButton(
            sub.subscriber.full_name, callback_data=str(sub.subscriber_id)
        ))
    await message.answer('Выберите подписчика', reply_markup=keyboard)


async def show_user_subs(callback: CallbackQuery, state: FSMContext):
    sub_user_id = int(callback.data)
    session_class: async_sessionmaker[AsyncSession] = callback.bot['session']
    async with session_class() as session:
        query_plan = (
            select(TrainingPlan.id)
            .where(TrainingPlan.trainer_id == callback.from_user.id)
        )
        plan_ids = (await session.execute(query_plan)).scalars().all()
        query = (
            select(TrainingSubscription)
            .where(and_(
                TrainingSubscription.plan_id.in_(plan_ids),
                TrainingSubscription.subscriber_id == sub_user_id,
                TrainingSubscription.balance > 0
            ))
        )
        result = (await session.execute(query)).scalars().all()
    await state.finish()
    text = '\n\n'.join(map(lambda obj: obj.display_text_buyer(), result))
    await callback.bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )
    await callback.bot.send_message(
        callback.from_user.id,
        text,
    )


async def add_count_manual_command(message: Message):
    session_class: async_sessionmaker[AsyncSession] = message.bot['session']
    async with session_class() as session:
        user_plans_ids = (await session.execute(
            select(TrainingPlan.id)
            .where(
                TrainingPlan.trainer_id == message.from_user.id
            )
        )).scalars().all()
        user_subs = (await session.execute(
            select(TrainingSubscription)
            .where(TrainingSubscription.plan_id.in_(user_plans_ids))
            .distinct(TrainingSubscription.subscriber_id)
        )).scalars().all()
    if not user_subs:
        await message.answer('У вас нет подписчиков')
        return
    await AddTrainingSessionCountState.choose_user.set()
    keyboard = InlineKeyboardMarkup()
    for sub in user_subs:
        keyboard.add(InlineKeyboardButton(
            sub.subscriber.full_name, callback_data=str(sub.subscriber_id)
        ))
    await message.answer(
        'Отлично! Выберите пользователя', reply_markup=keyboard
    )


async def choose_user_callback(callback: CallbackQuery):
    user_id = int(callback.data)
    session_class: async_sessionmaker[AsyncSession] = callback.bot['session']
    async with session_class() as session:
        user_plans_ids = (await session.execute(
            select(TrainingPlan.id)
            .where(
                TrainingPlan.trainer_id == callback.from_user.id
            )
        )).scalars().all()
        subscriptions = (await session.execute(
            select(TrainingSubscription)
            .where(and_(
                TrainingSubscription.plan_id.in_(user_plans_ids),
                TrainingSubscription.subscriber_id == user_id
            ))
        )).scalars().all()
    await AddTrainingSessionCountState.choose_plan.set()
    keyboard = InlineKeyboardMarkup()
    for sub in subscriptions:
        keyboard.add(InlineKeyboardButton(
            sub.inline_btn_text(), callback_data=str(sub.id)
        ))
    await callback.bot.send_message(
        callback.from_user.id, 'Выберите подписку', reply_markup=keyboard
    )
    await callback.bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )


async def choose_subscription_callback(
        callback: CallbackQuery, state: FSMContext
):
    await state.update_data(choose_plan=int(callback.data))
    await AddTrainingSessionCountState.add_count.set()
    await callback.bot.send_message(
        callback.from_user.id,
        'Отправьте кол-во начисляемых тренировок'
    )
    await callback.bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )


async def set_user_balance(message: Message, state: FSMContext):
    async with state.proxy() as data:
        sub_id = data['choose_plan']
    session_class: async_sessionmaker[AsyncSession] = message.bot['session']
    async with session_class() as session:
        sub: TrainingSubscription | None = await TrainingSubscription.select(
            session, {'id': sub_id}, True
        )
        if not sub:
            await message.answer('Подписка не найдена')
            await state.finish()
            return
        sub.balance += int(message.text)
        await session.commit()
    await message.answer(f'Успешно начислил {message.text} шт.')


def register_trainer_subscribe_handlers(dp: Dispatcher):
    dp.register_message_handler(
        remove_count_manual_command,
        text=TrainerButtonCommands.remove_training_manual.value,
        is_trainer=True
    )
    dp.register_message_handler(
        remove_count_manual_command,
        commands=[UserCommands.remove.name]
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
    dp.register_callback_query_handler(
        show_user_subs, state=ShowTrainerSubsState.choose_user
    )
    dp.register_message_handler(
        add_count_manual_command,
        text=TrainerButtonCommands.add_training_count.value
    )
    dp.register_callback_query_handler(
        choose_user_callback, state=AddTrainingSessionCountState.choose_user
    )
    dp.register_callback_query_handler(
        choose_subscription_callback,
        state=AddTrainingSessionCountState.choose_plan
    )
    dp.register_message_handler(
        set_user_balance, state=AddTrainingSessionCountState.add_count
    )

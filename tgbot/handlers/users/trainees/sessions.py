from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from tgbot.buttons.inline import make_yes_inline_btn, make_no_inline_btn
from tgbot.constants.commands import TraineeButtonCommands
from tgbot.keyboards.inline import make_inline_kb_from_objects_list
from tgbot.misc.states import StartTrainState
from tgbot.models.sessions import TrainingSession
from tgbot.models.subscribe import TrainingSubscription


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
        history = await TrainingSession.select(
            session, in_filters={'subscription_id': subs_ids},
        )
        if not history:
            await message.answer('Вы не посещали тренировки')
            return
    await message.answer(
        '<b>История тренировок</b>\n\n' +
        '\n\n'.join(map(lambda obj: obj.display_text(), history))
    )


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

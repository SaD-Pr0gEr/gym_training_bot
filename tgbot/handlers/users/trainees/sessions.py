from io import BytesIO

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from qrcode.image.pil import PilImage
from qrcode.main import make as make_qr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from tgbot.constants.commands import TraineeButtonCommands
from tgbot.keyboards.inline import make_inline_kb_from_objects_list
from tgbot.misc.states import StartTrainState
from tgbot.models.sessions import TrainingSession
from tgbot.models.subscribe import TrainingSubscription
from tgbot.utils.bot import make_start_training_deep_link


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
    await callback.bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )
    buf = BytesIO()
    qr: PilImage = make_qr(make_start_training_deep_link(
        await callback.bot.get_me(), f'{sub_id}'
    ))
    qr.save(buf, format='PNG')
    buf.seek(0)
    await callback.bot.send_photo(
        callback.from_user.id, buf,
        caption='Тренер должен отсканировать этот QR'
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

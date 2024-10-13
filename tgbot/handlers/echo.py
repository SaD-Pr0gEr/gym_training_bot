from datetime import datetime

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from tgbot.models.subscribe import TrainingSubscription
from tgbot.models.training import TrainingPlan


async def bot_echo(message: types.Message):
    text = [
        'Неизвестная команда:',
        message.text,
    ]
    await message.answer('\n'.join(text))


async def bot_echo_all(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
        'Сбросил незавершенный диалог. Попробуйте заново ввести команду'
    )


async def handle_other_callbacks(callback: CallbackQuery):
    session_class: async_sessionmaker[AsyncSession] = callback.bot['session']
    if callback.data.startswith('yes') or callback.data.startswith('no'):
        status, plan_id, buyer_id, trainer_id = callback.data.split('__')
        plan_id, buyer_id, trainer_id = (
            int(plan_id), int(buyer_id), int(trainer_id)
        )
        async with session_class() as session:
            plan = await TrainingPlan.select(session, {'id': plan_id}, True)
        if status == 'yes':
            async with session_class() as session:
                subscribe: TrainingSubscription | None = (
                    await TrainingSubscription.select(
                        session,
                        {'subscriber_id': buyer_id, 'plan_id': plan_id}, True
                    )
                )
                if subscribe:
                    if subscribe.active:
                        await TrainingSubscription.update(
                            session, {'id': subscribe.id},
                            {
                                'buy_date': datetime.now(),
                                'balance': subscribe.balance + plan.count
                            }
                        )
                    else:
                        await TrainingSubscription.update(
                            session, {'id': subscribe.id},
                            {
                                'buy_date': datetime.now(),
                                'balance': plan.count
                            }
                        )
                else:
                    subscribe = TrainingSubscription(
                        buyer_id, plan_id, datetime.now(), plan.count
                    )
                    session.add(subscribe)
                await session.commit()
            await callback.bot.send_message(
                callback.from_user.id,
                'Успешно активировал пакет'
            )
            await callback.bot.send_message(
                buyer_id,
                'Тренер подтвердил покупку пакета тренировок! '
                'Можете посмотреть в списке покупок'
            )
        else:
            await callback.bot.send_message(
                callback.from_user.id,
                'Отменил запрос'
            )
            await callback.bot.send_message(
                buyer_id, 'Тренер отменил запрос на покупку плана'
            )
    await callback.bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )


def register_echo(dp: Dispatcher):
    dp.register_message_handler(bot_echo)
    dp.register_message_handler(
        bot_echo_all, state='*', content_types=types.ContentTypes.ANY
    )
    dp.register_callback_query_handler(
        handle_other_callbacks, state='*'
    )

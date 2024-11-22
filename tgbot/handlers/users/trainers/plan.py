from enum import Enum

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.constants.commands import TrainerButtonCommands
from tgbot.keyboards.inline import two_enums_value_inline_keyboard
from tgbot.misc.states import AddTrainingPlanState
from tgbot.models.training import (
    TrainingTypes, TrainingTypesDisplay, TrainingPlan
)


async def add_plan_command(message: Message):
    await AddTrainingPlanState.type.set()
    await message.answer(
        'Отлично! Выберите тип тренировки',
        reply_markup=two_enums_value_inline_keyboard(
            TrainingTypes, TrainingTypesDisplay
        )
    )


async def add_plan_count(callback: CallbackQuery, state: FSMContext):
    await state.update_data(type=callback.data)
    type_: Enum = getattr(TrainingTypes, callback.data)
    if type_.name in [
        TrainingTypes.one_time_split.name,
        TrainingTypes.one_time_personal.name
    ]:
        await state.finish()
        session_class = callback.bot['session']
        async with session_class() as session:
            plans = await TrainingPlan.select(
                session,
                {
                    'count': 1, 'type': type_,
                    'trainer_id': callback.from_user.id
                }
            )
            if plans:
                await callback.bot.send_message(
                    callback.from_user.id,
                    'У вас уже есть такой план'
                )
            else:
                session.add(TrainingPlan(
                    1, TrainingTypes(type_.value), callback.from_user.id
                ))
                await session.commit()
                await callback.bot.send_message(
                    callback.from_user.id,
                    'Успешно добавил план тренировки'
                )
    else:
        await state.update_data(type=callback.data)
        await AddTrainingPlanState.count.set()
        await callback.bot.send_message(
            callback.from_user.id,
            'Отправьте кол-во тренировок по этому плану'
        )
    await callback.bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )


async def get_training_count(message: Message, state: FSMContext):
    if not message.text.isdecimal():
        await message.answer('Введите целое число')
        return
    async with state.proxy() as data:
        type_ = getattr(TrainingTypes, data['type'])
    await state.finish()
    session_class = message.bot['session']
    async with session_class() as session:
        plans = await TrainingPlan.select(
            session,
            {
                'count': int(message.text),
                'type': type_,
                'trainer_id': message.from_user.id
            }
        )
        if plans:
            await message.answer(
                'У вас уже есть такой план'
            )
        else:
            session.add(TrainingPlan(
                int(message.text), type_, message.from_user.id
            ))
            await session.commit()
            await message.answer(
                'Успешно добавил план тренировки'
            )


async def training_list_command(message: Message):
    session_class = message.bot['session']
    async with session_class() as session:
        plans = await TrainingPlan.select(
            session, {'trainer_id': message.from_user.id}
        )
    if not plans:
        await message.answer('У вас нет тренировочных планов')
        return
    txt = '\n\n'.join(map(lambda obj: obj.display_text(), plans))
    await message.answer(txt)


def register_trainer_plans_handlers(dp: Dispatcher):
    dp.register_message_handler(
        add_plan_command, text=TrainerButtonCommands.add_plan.value,
        is_trainer=True
    )
    dp.register_callback_query_handler(
        add_plan_count, state=AddTrainingPlanState.type
    )
    dp.register_message_handler(
        get_training_count, state=AddTrainingPlanState.count
    )
    dp.register_message_handler(
        training_list_command, text=TrainerButtonCommands.plans_list.value
    )

from tgbot.models.training import TrainingPlan, TrainingTypesDisplay


def display_plan_text(plan: TrainingPlan) -> str:
    return (
        f'<b>{getattr(TrainingTypesDisplay, plan.type.name).value}</b>\n'
        f'Дней тренировок: {plan.count}'
    )

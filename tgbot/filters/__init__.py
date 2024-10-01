from .admin import AdminFilter
from .trainer import TrainerFilter


def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)
    dp.filters_factory.bind(TrainerFilter)

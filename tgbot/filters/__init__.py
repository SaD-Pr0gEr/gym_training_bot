from .admin import AdminFilter
from .trainer import TrainerFilter
from .user import LoggedUserFilter


def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)
    dp.filters_factory.bind(TrainerFilter)
    dp.filters_factory.bind(LoggedUserFilter)

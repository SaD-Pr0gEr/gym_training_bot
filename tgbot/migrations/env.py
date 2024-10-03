import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from environs import Env

from alembic import context

BASE_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(BASE_DIR))

from tgbot.config import PgDbConfig
from tgbot.models.base import Model
import tgbot.models.user
import tgbot.models.training
import tgbot.models.subscribe
import tgbot.models.sessions

config = context.config

env = Env()
env.read_env(str(BASE_DIR / '.env'))

db_config = PgDbConfig(
    host=env.str('DB_HOST'),
    port=env.str('DB_PORT'),
    password=env.str('DB_PASS'),
    user=env.str('DB_USER'),
    database=env.str('DB_NAME')
)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option(
    'sqlalchemy.url',
    db_config.db_url
)
target_metadata = Model.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata,
            include_schemas=True, compare_type=True,
            compare_server_default=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

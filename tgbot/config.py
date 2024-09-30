from dataclasses import dataclass
from pathlib import Path

from environs import Env


@dataclass(frozen=True)
class DbConfig:
    host: str
    port: int

    @property
    def db_url(self) -> str:
        raise NotImplementedError

    @property
    def db_url_async(self) -> str:
        raise NotImplementedError


@dataclass(frozen=True)
class PgDbConfig(DbConfig):
    password: str
    user: str
    database: str

    @property
    def db_url(self) -> str:
        return (
            f'postgresql://{self.user}:{self.password}@'
            f'{self.host}:{self.port}/{self.database}'
        )

    @property
    def db_url_async(self) -> str:
        return f'postgresql+asyncpg://' + self.db_url.split('//')[-1]


@dataclass(frozen=True)
class RedisDbConfig(DbConfig):
    password: str | None = None
    user: str | None = None
    database: str = '1'

    @property
    def db_url(self) -> str:
        url = 'redis://'
        if self.user is not None and self.password is not None:
            url += f'{self.user}:{self.password}@'
        url += f'f{self.host}:{self.port}/{self.database}'
        return url

    @property
    def db_url_async(self) -> str:
        return self.db_url


@dataclass(frozen=True)
class TgBot:
    token: str
    admin_ids: list[int]
    use_redis: bool


@dataclass(frozen=True)
class Misc:
    BASE_DIR: Path = Path(__file__).parent.parent


@dataclass(frozen=True)
class Config:
    tg_bot: TgBot
    db: DbConfig
    misc: Misc


def load_config(path: str | None = None):
    env = Env()
    if path:
        env.read_env(path)
    misc = Misc()
    return Config(
        tg_bot=TgBot(
            token=env.str('BOT_TOKEN'),
            admin_ids=env.list('ADMINS'),
            use_redis=env.bool('USE_REDIS'),
        ),
        misc=misc,
        db=PgDbConfig(
            host=env.str('DB_HOST'),
            port=env.str('DB_PORT'),
            password=env.str('DB_PASS'),
            user=env.str('DB_USER'),
            database=env.str('DB_NAME')
        )
    )

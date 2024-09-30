import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from tgbot.config import load_config
from tgbot.filters import register_all_filters
from tgbot.handlers import register_all_handlers
from tgbot.utils.bot import install_bot_commands

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=(
            u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - '
            u'%(name)s - %(message)s'
        )
    )
    logger.info('Starting bot')
    config = load_config('.env')
    storage = RedisStorage2() if config.tg_bot.use_redis else MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage)
    engine = create_async_engine(config.db.db_url_async)
    async_session = async_sessionmaker(engine)

    bot['config'] = config
    bot['session'] = async_session
    register_all_filters(dp)
    register_all_handlers(dp)
    await install_bot_commands(bot)

    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        session = await bot.get_session()
        await session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error('Bot stopped!')

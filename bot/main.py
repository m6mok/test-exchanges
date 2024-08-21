import logging
from os import getenv as os_getenv

from aiogram import Bot, Dispatcher, Router
from aiohttp import ClientSession as aiohttp_ClientSession
from asyncio import (
    run as asyncio_run,
    sleep as asyncio_sleep,
    create_task as asyncio_create_task
)

from database import Database
from handlers import register_handlers
from schedule import update_exchanges


logging.basicConfig(level=logging.WARNING)


async def main() -> None:
    token = os_getenv('TELEGRAM_BOT_TOKEN')
    if token is None:
        raise ValueError('No Telegram-bot token in environ')

    bot = Bot(token=token)
    dp = Dispatcher()
    
    # handlers
    router = Router()
    register_handlers(router)
    dp.include_router(router)

    # database
    db = Database(
        user=os_getenv('POSTGRES_USER'),
        password=os_getenv('POSTGRES_PASSWORD'),
        host=os_getenv('DATABASE_HOST'),
        port=os_getenv('DATABASE_PORT'),
        database_name=os_getenv('POSTGRES_DB')
    )
    await db.init_models()

    # schedule
    async def api_scheduler():
        token = os_getenv('CMC_TOKEN')
        if token is None:
            raise ValueError('No CMC token in environ')

        async with aiohttp_ClientSession() as session:
            while True:
                await asyncio_sleep(10)
                await update_exchanges(bot, session, token)
                await asyncio_sleep(50)
    asyncio_create_task(api_scheduler())

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio_run(main())


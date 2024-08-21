from aiogram import Bot
from aiohttp import (
    ClientSession as aiohttp_ClientSession
)

from database import Database
from database.queries import (
    get_user_ids_tracked_currency,
    update_currencies
)
from database.queries.types import CurrencyData


CMC_API_URL = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

CMC_API_PARAMS = {
    'start': '1',
    'limit': '10',
    'convert': 'USD'
}

CMC_API_HEADERS = {
    'Accept': 'application/json'
}


async def update_exchanges(bot: Bot, session: aiohttp_ClientSession, token: str):    
    CMC_API_HEADERS['X-CMC_PRO_API_KEY'] = token

    async with session.get(
        CMC_API_URL,
        headers=CMC_API_HEADERS,
        params=CMC_API_PARAMS
    ) as response:
        response.raise_for_status()
        json_data = await response.json()
        currency_data = [
            CurrencyData(
                id=item['id'],
                slug=item['slug'],
                symbol=item['symbol'],
                usdt_price=item['quote']['USD']['price']
            )
            for item in json_data['data']
        ]

    async with Database.instance.session() as session:
        for currency in currency_data:
            choices = await get_user_ids_tracked_currency(
                session,
                currency.id,
                currency.usdt_price
            )
            
            await update_currencies(
                session,
                currency_data
            )

            for choice in choices:
                await bot.send_message(
                    choice.user_id,
                    (
                        f'{currency.slug} ({currency.symbol})\n' +
                        f'!   *${choice.threshold:.2f} ' +
                        ('>' if choice.threshold > currency.usdt_price else '<') +
                        f' ${currency.usdt_price:.2f}'
                    )
                )

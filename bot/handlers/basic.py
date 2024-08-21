from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from database import Database
from handlers.markups import main_reply_markup
from handlers.shortcuts import process_user
from handlers.states import TrackStates


async def start(message: Message, state: FSMContext):
    async with Database.instance.session() as session:
        await process_user(session, message)

    await message.answer(
        'Добро пожаловать!',
        reply_markup=main_reply_markup()
    )
    await message.answer('Пожалуйста, напишите тикер для отслеживания')
    await state.set_state(TrackStates.TickerChoose)


async def help(message: Message, state: FSMContext):
    async with Database.instance.session() as session:
        await process_user(session, message)
    
    await message.answer(
        'Тикер - краткое название в биржевой информации (bitcoin - BTC)\n'
        'Минимальный порог значения валюты - когда валюта опускается ниже поставленного уровня\n'
        'Максимальный порог значения валюты - когда валюта поднимается выше поставленного уровня\n\n'
        '/choose_ticker Добавить валюту к отслеживанию\n'
        '/untrack_ticker Не отслеживать валюту\n'
        '/get_choices Показать все текущие отслеживаемые валюты'
    )

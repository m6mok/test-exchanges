from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from aiogram.fsm.context import FSMContext

from database import Database
from database.queries import (
    add_user_choices,
    delete_user_choices,
    get_currency_id,
    get_user_choices,
)
from database.queries.types import CurrencyChoice
from handlers.markups import main_reply_markup
from handlers.shortcuts import process_user
from handlers.states import TrackStates, UntrackStates


async def begin_choose_ticker(message: Message, state: FSMContext):
    async with Database.instance.session() as session:
        await process_user(session, message)

    await state.set_state(TrackStates.TickerChoose)
    await message.answer('Задайте тикер валюты')


async def choose_ticker(message: Message, state: FSMContext):
    symbol = message.text
    currency_id = None

    async with Database.instance.session() as session:
        await process_user(session, message)

        currency_id = await get_currency_id(session, symbol)

        if currency_id is None:
            await message.answer(f'Тикер `{symbol}` не найден')
            await state.clear()
            return

    await state.set_data({
        'symbol': symbol,
        'currency_id': currency_id
    })
    await state.set_state(TrackStates.ThresholdChoose)
    await message.answer('Задайте пороговое значение валюты')


async def get_threshold(message: Message, state: FSMContext):
    try:
        threshold = float(message.text)
    except ValueError:
        threshold = None
    
    if isinstance(threshold, float) and threshold <= 0:
        threshold = None

    async with Database.instance.session() as session:
        await process_user(session, message)

    if threshold is None:
        await message.answer(
            f'Значение `{message.text}` не является числом. '
            'Тикер не добавлен к отслеживаемым'
        )
        await state.clear()
        return

    await state.update_data({
        'threshold': threshold,
    })
    await state.set_state(TrackStates.IsFloorChoose)
    await message.answer(
        'Выбранное тип порогового значения',
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='Минимальное'),
                    KeyboardButton(text='Максимальное')
                ]
            ],
            resize_keyboard=True
        )
    )


async def get_is_floor(message: Message, state: FSMContext):
    if message.text == 'Минимальное':
        is_floor = True
    elif message.text == 'Максимальное':
        is_floor = False
    else:
        is_floor = None

    async with Database.instance.session() as session:
        await process_user(session, message)

        if is_floor is None:
            await message.answer(
                f'Значение `{message.text}` не является ответом '
                ' (Минимальное/Максимальное). '
                'Тикер не добавлен к отслеживаемым'
            )
            await state.clear()
            return

        state_data = await state.get_data()
        symbol = state_data['symbol']
        threshold = state_data['threshold']
        currency_id = state_data['currency_id']

        await add_user_choices(
            session,
            message.from_user.id,
            (CurrencyChoice(
                currency_id=currency_id,
                threshold=threshold,
                is_floor=is_floor
            ),)
        )
        await message.answer(
            f'Тикер `{symbol}` добавлен к отслеживаемым с ' +
            ('минимальным' if is_floor else 'максимальным') +
            f' порогом `${threshold}`',
            reply_markup=main_reply_markup()
        )

    await state.clear()


async def get_choices(message: Message, state: FSMContext):
    async with Database.instance.session() as session:
        await process_user(session, message)

        response = await get_user_choices(session, message.from_user.id)

    if response:
        await message.answer(
            'Отслеживаемые валюты:\n' +
            '\n'.join(
                f'{currency.slug} ({currency.symbol})\n' +
                (
                    '!   ' if (
                        currency.threshold > currency.usdt_price and currency.is_floor or
                        currency.threshold < currency.usdt_price and not currency.is_floor
                    ) else '    '
                ) +
                f'*${currency.threshold:.2f} ' +
                ('>' if currency.is_floor else '<') +
                f' ${currency.usdt_price:.2f}'
                for currency in response.currencies
            )
        )
    else:
        await message.answer('Отслеживаемые валюты не найдены')


async def begin_untrack_ticker(message: Message, state: FSMContext):
    async with Database.instance.session() as session:
        await process_user(session, message)

    await message.answer('Укажите тикер валюты для отмены отслеживания')
    await state.set_state(UntrackStates.TickerChoose)


async def untrack_ticker(message: Message, state: FSMContext):
    symbol = message.text

    async with Database.instance.session() as session:
        await process_user(session, message)

        currency_id = await get_currency_id(session, symbol)

        if currency_id is not None:
            await delete_user_choices(
                session,
                message.from_user.id,
                (currency_id,)
            )
            await message.answer(f'Тикер {symbol} удалён из отслеживаемых')
        else:
            await message.answer(f'Тикер {symbol} не найден')

    await state.clear()


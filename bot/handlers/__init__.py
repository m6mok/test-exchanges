from aiogram import Router, F
from aiogram.filters import CommandStart, Command

from handlers.basic import start, help
from handlers.views import (
    begin_choose_ticker,
    begin_untrack_ticker,
    choose_ticker,
    get_choices,
    get_is_floor,
    get_threshold,
    untrack_ticker
)
from handlers.states import TrackStates, UntrackStates


def register_handlers(router: Router) -> None:
    router.message.register(start, CommandStart())
    router.message.register(help, Command('help'))
    router.message.register(begin_choose_ticker, Command('choose_ticker'))
    router.message.register(begin_untrack_ticker, Command('untrack_ticker'))
    router.message.register(get_choices, Command('get_choices'))

    router.message.register(choose_ticker, F.text, TrackStates.TickerChoose)
    router.message.register(get_threshold, F.text, TrackStates.ThresholdChoose)
    router.message.register(get_is_floor, F.text, TrackStates.IsFloorChoose)
    router.message.register(untrack_ticker, F.text, UntrackStates.TickerChoose)

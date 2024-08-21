from aiogram.fsm.state import State, StatesGroup


class TrackStates(StatesGroup):
    TickerChoose = State()
    ThresholdChoose = State()
    IsFloorChoose = State()


class UntrackStates(StatesGroup):
    TickerChoose = State()

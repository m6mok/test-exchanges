from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_reply_markup() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='/help')],
            [
                KeyboardButton(text='/choose_ticker'),
                KeyboardButton(text='/untrack_ticker')
            ],
            [KeyboardButton(text='/get_choices')],
        ],
        resize_keyboard=True
    )

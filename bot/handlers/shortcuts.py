from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.queries import (
    user_not_exists,
    update_user_last_visit,
    add_user
)
from database.queries.types import UserData


async def process_user(session: AsyncSession, message: Message) -> None:
    if await user_not_exists(session, message.from_user.id):
        await add_user(
            session,
            UserData(tg_id=message.from_user.id, chat_id=message.chat.id)
        )
    await update_user_last_visit(session, message.from_user.id)

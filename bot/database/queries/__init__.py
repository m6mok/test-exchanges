from datetime import datetime

from sqlalchemy import update, func, and_, select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import aliased

from database.queries.types import (
    CurrencyChoiceData,
    CurrencyChoice,
    CurrencyData,
    UserChoicesResponse,
    UserChoiceResponse,
    UserData,
)
from database.models import User, Currency, CurrencyUpdate, UserChoice


async def get_currency_id(
    session: AsyncSession,
    symbol: str
) -> int | None:
    result = await session.execute(
        select(Currency.id)
            .where(Currency.symbol == symbol)
    )
    return result.scalar_one_or_none()


async def update_currencies(
    session: AsyncSession,
    currencies: list[CurrencyData]
) -> None:
    for currency_data in currencies:
        result = await session.execute(
            insert(Currency)
                .values(
                    id=currency_data.id,
                    slug=currency_data.slug,
                    symbol=currency_data.symbol
                )
                .on_conflict_do_nothing()
                .returning(Currency.id)
        )

        if (currency_id := result.scalar_one_or_none()):
            session.add(
                CurrencyUpdate(
                    currency_id=currency_id,
                    usdt_price=currency_data.usdt_price
                )
            )

    await session.commit()


async def get_user_ids_tracked_currency(
    session: AsyncSession,
    currency_id: int,
    usdt_price: float
) -> list[UserChoice]:
    result_floor = await session.execute(
        select(UserChoice.user_id, UserChoice.threshold)
            .where(
                UserChoice.currency_id == currency_id,
                UserChoice.is_floor,
                UserChoice.threshold > usdt_price
            )
    )
    result_ceiling = await session.execute(
        select(UserChoice.user_id, UserChoice.threshold)
            .where(
                UserChoice.currency_id == currency_id,
                ~UserChoice.is_floor,
                UserChoice.threshold < usdt_price
            )
    )
    return [
        UserChoiceResponse(user_id=row[0], threshold=row[1])
        for row in set(result_floor.all() + result_ceiling.all())
    ]


async def add_user(
    session: AsyncSession,
    user_data: UserData
) -> None:
    session.add(
        User(tg_id=user_data.tg_id, chat_id=user_data.chat_id)
    )
    await session.commit()


async def user_not_exists(
    session: AsyncSession,
    tg_id: int
) -> bool:
    result = await session.execute(
        select(User.tg_id)
            .where(User.tg_id == tg_id)
    )
    return result.scalar_one_or_none() is None


async def update_user_last_visit(
    session: AsyncSession,
    tg_id: int
) -> None:
    await session.execute(
        update(User)
            .where(User.tg_id == tg_id)
            .values(last_visit=datetime.now())
    )
    await session.commit()


async def add_user_choices(
    session: AsyncSession,
    tg_id: int,
    currency_choices: list[CurrencyChoice]
) -> None:
    for choice in currency_choices:
        await session.execute(
            delete(UserChoice)
                .where(
                    UserChoice.user_id == tg_id,
                    UserChoice.currency_id == choice.currency_id,
                    UserChoice.is_floor == choice.is_floor,
                )
        )
        session.add(
            UserChoice(
                user_id=tg_id,
                threshold=choice.threshold,
                is_floor=choice.is_floor,
                currency_id=choice.currency_id,
            )
        )
    await session.commit()


async def delete_user_choices(
    session: AsyncSession,
    tg_id: int,
    currency_ids: list[int]
) -> None:
    for currency_id in currency_ids:
        await session.execute(
            delete(UserChoice)
                .where(
                    UserChoice.user_id == tg_id,
                    UserChoice.currency_id == currency_id
                )
        )
    await session.commit()


async def get_user_choices(
    session: AsyncSession,
    tg_id: int
) -> UserChoicesResponse | None:
    latest_update_subquery = (
        select(
            CurrencyUpdate.currency_id,
            func.max(CurrencyUpdate.timestamp).label('latest_timestamp')
        )
        .group_by(CurrencyUpdate.currency_id)
        .subquery()
    )

    latest_currency_update = aliased(CurrencyUpdate)

    result = await session.execute(
        select(
            Currency.slug,
            Currency.symbol,
            latest_currency_update.usdt_price,
            UserChoice.threshold,
            UserChoice.is_floor
        )
        .join(UserChoice, Currency.id == UserChoice.currency_id)
        .join(
            latest_currency_update,
            and_(
                Currency.id == latest_currency_update.currency_id,
                latest_currency_update.timestamp == select(
                    latest_update_subquery.c.latest_timestamp
                )
                    .where(latest_update_subquery.c.currency_id == Currency.id)
                    .scalar_subquery()
            )
        )
        .where(UserChoice.user_id == tg_id)
    )

    rows = result.all()
    return UserChoicesResponse(
        currencies=[
            CurrencyChoiceData(
                slug=row[0],
                symbol=row[1],
                usdt_price=row[2],
                threshold=row[3],
                is_floor=row[4]
            ) 
            for row in rows
        ]
    ) if rows else None

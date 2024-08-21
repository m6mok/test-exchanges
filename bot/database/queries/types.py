from pydantic import BaseModel


class CurrencyName(BaseModel):
    id: int
    slug: str
    symbol: str


class CurrencyChoice(BaseModel):
    currency_id: int
    threshold: float
    is_floor: bool


class CurrencyData(BaseModel):
    id: int
    slug: str
    symbol: str
    usdt_price: float


class CurrencyChoiceData(BaseModel):
    slug: str
    symbol: str
    usdt_price: float
    threshold: float
    is_floor: float


class UserData(BaseModel):
    tg_id: int
    chat_id: int


class UserChoiceResponse(BaseModel):
    user_id: int
    threshold: float


class UserChoicesResponse(BaseModel):
    currencies: list[CurrencyChoiceData]

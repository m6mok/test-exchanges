from sqlalchemy.orm import relationship
from sqlalchemy.orm.decl_api import DeclarativeBase
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    TIMESTAMP,
    Float,
    Boolean
)
from datetime import datetime


Base: DeclarativeBase = declarative_base()


class User(Base):
    __tablename__ = 'user'
    
    tg_id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, nullable=False)
    timestamp = Column(TIMESTAMP, default=datetime.now)
    last_visit = Column(TIMESTAMP)

    choices = relationship("UserChoice", back_populates="user")


class Currency(Base):
    __tablename__ = 'currency'
    
    id = Column(Integer, primary_key=True, unique=True)
    slug = Column(String, nullable=False, unique=True)
    symbol = Column(String, nullable=False, unique=True)

    updates = relationship("CurrencyUpdate", back_populates="currency")


class CurrencyUpdate(Base):
    __tablename__ = 'currency_updates'

    id = Column(Integer, primary_key=True, autoincrement=True)
    currency_id = Column(Integer, ForeignKey('currency.id'), nullable=False)
    usdt_price = Column(Float, nullable=False)
    timestamp = Column(TIMESTAMP, default=datetime.now)

    currency = relationship("Currency", back_populates="updates")


class UserChoice(Base):
    __tablename__ = 'user_choice'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.tg_id'), nullable=False)

    threshold = Column(Float, nullable=False)
    is_floor = Column(Boolean, nullable=False)
    currency_id = Column(Integer, ForeignKey('currency.id'), nullable=False)

    user = relationship("User", back_populates="choices")
    currency = relationship("Currency")

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from db.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    login: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)


class Strategy(Base):
    __tablename__ = "strategies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    bots: Mapped[List["Bot"]] = relationship(back_populates="strategy", cascade="all, delete-orphan")
    backtests: Mapped[List["BacktestResult"]] = relationship(
        back_populates="strategy", cascade="all, delete-orphan"
    )


class Bot(Base):
    __tablename__ = "bots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    additional_info: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    money_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    money_symbol: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    strategy_id: Mapped[int] = mapped_column(ForeignKey("strategies.id"), nullable=False, index=True)
    strategy: Mapped["Strategy"] = relationship(back_populates="bots")

    symbols: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class BacktestResult(Base):
    __tablename__ = "backtest_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    strategy_id: Mapped[int] = mapped_column(ForeignKey("strategies.id"), nullable=False, index=True)
    strategy: Mapped["Strategy"] = relationship(back_populates="backtests")

    test_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    dataset_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Text field to store JSON 
    results: Mapped[str] = mapped_column(Text, nullable=False)


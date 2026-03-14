from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import Bot, Strategy
from db.session import get_db
from executor.runtime_registry import BotRuntimeRegistry

router = APIRouter(prefix="/bots", tags=["Bots"])


class BotCreateRequest(BaseModel):
    name: str
    strategy_id: int
    symbols: list[str]


class BotUpdateRequest(BaseModel):
    name: str | None = None
    strategy_id: int | None = None
    symbols: list[str] | None = None


class BotResponse(BaseModel):
    id: int
    name: str
    strategy_id: int
    strategy_name: str
    symbols: list[str]
    started_at: datetime


def _get_runtime_registry(request: Request) -> BotRuntimeRegistry:
    registry = getattr(request.app.state, "bot_runtime_registry", None)
    if registry is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Bot runtime is not initialized",
        )
    return registry


def _require_strategy(db: Session, strategy_id: int) -> Strategy:
    strategy = db.get(Strategy, strategy_id)
    if strategy is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Strategy not found")
    return strategy


def _to_response(bot: Bot, strategy_name: str) -> BotResponse:
    return BotResponse(
        id=bot.id,
        name=bot.name,
        strategy_id=bot.strategy_id,
        strategy_name=strategy_name,
        symbols=bot.symbols,
        started_at=bot.started_at,
    )


@router.get("", response_model=list[BotResponse])
def list_bots(db: Session = Depends(get_db)) -> list[BotResponse]:
    rows = db.execute(select(Bot, Strategy.name).join(Strategy, Bot.strategy_id == Strategy.id)).all()
    return [_to_response(bot=row[0], strategy_name=row[1]) for row in rows]


@router.get("/{bot_id}", response_model=BotResponse)
def get_bot(bot_id: int, db: Session = Depends(get_db)) -> BotResponse:
    row = db.execute(
        select(Bot, Strategy.name).join(Strategy, Bot.strategy_id == Strategy.id).where(Bot.id == bot_id)
    ).first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")
    return _to_response(bot=row[0], strategy_name=row[1])


@router.post("", response_model=BotResponse, status_code=status.HTTP_201_CREATED)
def create_bot(
    payload: BotCreateRequest,
    db: Session = Depends(get_db),
    runtime_registry: BotRuntimeRegistry = Depends(_get_runtime_registry),
) -> BotResponse:
    strategy = _require_strategy(db, payload.strategy_id)

    bot = Bot(name=payload.name, strategy_id=payload.strategy_id, symbols=payload.symbols)
    db.add(bot)

    try:
        db.flush()
        runtime_registry.create(bot.id, bot.name, bot.symbols, strategy)
    except ValueError as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    try:
        db.commit()
    except Exception:
        db.rollback()
        runtime_registry.delete(bot.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to persist bot",
        )

    db.refresh(bot)
    return _to_response(bot=bot, strategy_name=strategy.name)


@router.put("/{bot_id}", response_model=BotResponse)
def update_bot(
    bot_id: int,
    payload: BotUpdateRequest,
    db: Session = Depends(get_db),
    runtime_registry: BotRuntimeRegistry = Depends(_get_runtime_registry),
) -> BotResponse:
    bot = db.get(Bot, bot_id)
    if bot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")

    previous_name = bot.name
    previous_symbols = list(bot.symbols)
    previous_strategy = bot.strategy

    strategy = bot.strategy

    if payload.name is not None:
        bot.name = payload.name
    if payload.strategy_id is not None:
        strategy = _require_strategy(db, payload.strategy_id)
        bot.strategy_id = payload.strategy_id
    if payload.symbols is not None:
        bot.symbols = payload.symbols

    try:
        runtime_registry.update(bot.id, bot.name, bot.symbols, strategy)
    except ValueError as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    try:
        db.commit()
    except Exception:
        db.rollback()
        runtime_registry.update(bot.id, previous_name, previous_symbols, previous_strategy)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to persist bot update",
        )

    db.refresh(bot)
    return _to_response(bot=bot, strategy_name=strategy.name)


@router.delete("/{bot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bot(
    bot_id: int,
    db: Session = Depends(get_db),
    runtime_registry: BotRuntimeRegistry = Depends(_get_runtime_registry),
) -> None:
    bot = db.get(Bot, bot_id)
    if bot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")

    strategy = bot.strategy
    name = bot.name
    symbols = list(bot.symbols)

    runtime_registry.delete(bot.id)

    db.delete(bot)
    try:
        db.commit()
    except Exception:
        db.rollback()
        runtime_registry.create(bot_id, name, symbols, strategy)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete bot",
        )

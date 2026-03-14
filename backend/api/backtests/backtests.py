from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import BacktestResult, Strategy
from db.session import get_db

router = APIRouter(prefix="/backtests", tags=["Backtests"])


class BacktestCreateRequest(BaseModel):
    strategy_id: int
    dataset_name: str
    results: str


class BacktestUpdateRequest(BaseModel):
    strategy_id: int | None = None
    dataset_name: str | None = None
    results: str | None = None


class BacktestResponse(BaseModel):
    id: int
    strategy_id: int
    strategy_name: str
    test_time: datetime
    dataset_name: str
    results: str


def _require_strategy(db: Session, strategy_id: int) -> Strategy:
    strategy = db.get(Strategy, strategy_id)
    if strategy is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Strategy not found")
    return strategy


def _to_response(backtest: BacktestResult, strategy_name: str) -> BacktestResponse:
    return BacktestResponse(
        id=backtest.id,
        strategy_id=backtest.strategy_id,
        strategy_name=strategy_name,
        test_time=backtest.test_time,
        dataset_name=backtest.dataset_name,
        results=backtest.results,
    )


@router.get("", response_model=list[BacktestResponse])
def list_backtests(db: Session = Depends(get_db)) -> list[BacktestResponse]:
    rows = (
        db.execute(
            select(BacktestResult, Strategy.name)
            .join(Strategy, BacktestResult.strategy_id == Strategy.id)
            .order_by(BacktestResult.id.asc())
        )
        .all()
    )
    return [_to_response(backtest=row[0], strategy_name=row[1]) for row in rows]


@router.get("/{backtest_id}", response_model=BacktestResponse)
def get_backtest(backtest_id: int, db: Session = Depends(get_db)) -> BacktestResponse:
    row = db.execute(
        select(BacktestResult, Strategy.name)
        .join(Strategy, BacktestResult.strategy_id == Strategy.id)
        .where(BacktestResult.id == backtest_id)
    ).first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Backtest result not found")
    return _to_response(backtest=row[0], strategy_name=row[1])


@router.post("", response_model=BacktestResponse, status_code=status.HTTP_201_CREATED)
def create_backtest(payload: BacktestCreateRequest, db: Session = Depends(get_db)) -> BacktestResponse:
    strategy = _require_strategy(db, payload.strategy_id)

    backtest = BacktestResult(
        strategy_id=payload.strategy_id,
        dataset_name=payload.dataset_name,
        results=payload.results,
    )
    db.add(backtest)
    db.commit()
    db.refresh(backtest)
    return _to_response(backtest=backtest, strategy_name=strategy.name)


@router.put("/{backtest_id}", response_model=BacktestResponse)
def update_backtest(
    backtest_id: int,
    payload: BacktestUpdateRequest,
    db: Session = Depends(get_db),
) -> BacktestResponse:
    backtest = db.get(BacktestResult, backtest_id)
    if backtest is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Backtest result not found")

    strategy_name = backtest.strategy.name

    if payload.strategy_id is not None:
        strategy = _require_strategy(db, payload.strategy_id)
        backtest.strategy_id = payload.strategy_id
        strategy_name = strategy.name
    if payload.dataset_name is not None:
        backtest.dataset_name = payload.dataset_name
    if payload.results is not None:
        backtest.results = payload.results

    db.commit()
    db.refresh(backtest)
    return _to_response(backtest=backtest, strategy_name=strategy_name)


@router.delete("/{backtest_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_backtest(backtest_id: int, db: Session = Depends(get_db)) -> None:
    backtest = db.get(BacktestResult, backtest_id)
    if backtest is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Backtest result not found")

    db.delete(backtest)
    db.commit()

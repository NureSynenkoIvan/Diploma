from fastapi import APIRouter
from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import Strategy
from db.session import get_db

router = APIRouter(prefix="/strategies", tags=["Strategies"])


class StrategyResponse(BaseModel):
    id: int
    name: str
    description: str | None
    symbols_required: int
    timeframe: str


@router.get("", response_model=list[StrategyResponse])
async def list_strategies(db: Session = Depends(get_db)) -> list[StrategyResponse]:
    rows = db.execute(select(Strategy).order_by(Strategy.name.asc())).scalars().all()
    return [
        StrategyResponse(
            id=row.id,
            name=row.name,
            description=row.description,
            symbols_required=row.symbols_required,
            timeframe=row.timeframe,
        )
        for row in rows
    ]

@router.get("/names")
async def list_strategy_names(db: Session = Depends(get_db)):
    rows = db.execute(select(Strategy.name).order_by(Strategy.name.asc())).all()
    return {"available_strategies": [r[0] for r in rows]}
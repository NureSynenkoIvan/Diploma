import json

from sqlalchemy.orm import Session

from app.background_tasks.celery_app import celery
from app.backtest.BacktestEngine import BacktestEngine
from app.backtest.BacktestResult import BacktestResult


@celery.task(bind=True, name="backtest_from_file")
def backtest_from_file_task(runtime_strategy,
    money_amount: float,
    money_symbol: str,
    dataset_name: str,
    dataset_file,
    db: Session):
    engine = BacktestEngine()
    engine_result = engine.run(runtime_strategy, dataset_file, money_amount, money_symbol)

    resolved_dataset_name = dataset_name or dataset_file.filename or f"manual-{datetime.utcnow().isoformat()}"

    results_json = json.dumps({
        'overall_profit_percent': engine_result.overall_profit_percent,
        'mean_monthly_profit_percent': engine_result.mean_monthly_profit_percent,
        'max_drawdown_percent': engine_result.max_drawdown_percent,
        'win_rate_percent': engine_result.win_rate_percent,
    })

    backtest = BacktestResult(
        strategy_id="",
        dataset_name=resolved_dataset_name,
        results=results_json,
    )
    db.add(backtest)
    db.commit()
    db.refresh(backtest)
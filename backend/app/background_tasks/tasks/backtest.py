import json
from datetime import datetime

from celery import shared_task
from sqlalchemy import select

from app.data.database import BacktestResult
from app.strategies.registry import STRATEGY_CLASSES

from app.backtest.BacktestEngine import BacktestEngine
from app.data.data_provider import MarketDataProvider, GapsFoundError, OHLCVDataProvider
from app.strategies.Strategy import Strategy
from app.utils.timeframe import get_candles_left
from app.data.database.models import Strategy as StrategyModel, BacktestResult
from app.data.database.session import db_session


MAX_RECURSION_DEPTH = 4

def approximate_wait_time(start_date, end_date, timeframe):
    timeframe = get_candles_left(start_date, end_date, timeframe)
    return timeframe / 1000

def load_historical_data(strategy : Strategy, start_date : datetime, end_date : datetime) -> MarketDataProvider:
    """Currently assumes all these things are in strategy"""
    schema = strategy.get_parameters_schema()
    schema_keys = {item['key'] for item in schema}

    required = {'symbol', 'exchange', 'timeframe'}
    has_required = required.issubset(schema_keys)

    if has_required:
        exchange = getattr(strategy, 'exchange')
        symbol = getattr(strategy, 'symbol')
        timeframe = getattr(strategy, 'timeframe')

        return OHLCVDataProvider(strategy, start_date, end_date, exchange, symbol, timeframe)
    else:
        missing = required - schema_keys
        raise Exception(f"Strategy is missing required parameters: {missing}")


@shared_task(bind=True, name="backtest_celery")
def backtest_task(self, strategy_name : str, strategy_dict : dict, start_date : datetime, end_date : datetime, money_amount : float, retry_number=0):
    try:
        print("Starting backtest ...")
        strategy_class = STRATEGY_CLASSES[strategy_name]
        strategy = strategy_class(**strategy_dict)
        data_provider = load_historical_data(strategy, start_date, end_date)
        engine = BacktestEngine()
        result = engine.run(strategy, data_provider, money_amount)

        results_json = json.dumps({
            'overall_profit_percent': result.overall_profit_percent,
            'mean_monthly_profit_percent': result.mean_monthly_profit_percent,
            'max_drawdown_percent': result.max_drawdown_percent,
            'win_rate_percent': result.win_rate_percent,
        })
        with db_session() as db:
            strategy_record = db.execute(
                select(StrategyModel).where(StrategyModel.name == strategy_name)
            ).scalar_one_or_none()

            if not strategy_record:
                print(f"Error: Strategy {strategy_name} not found in database.")
                return

            backtest = BacktestResult(
                strategy_id=strategy_record.id,
                dataset_name=f"{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}_{strategy_name}",
                results=results_json,
                test_time=datetime.now()

            )
            result_id = backtest.id
            db.add(backtest)
            print("Backtest results saved successfully.")
            return {"status": "success", "backtest_id": result_id}

    except GapsFoundError as e:
        wait_time = 0
        for gap in e.gaps:
            wait_time += approximate_wait_time(gap[0], gap[1], e.timeframe)
            print(f"Data not present in DB! Backfill tasks launched, retrying in {wait_time} seconds")
            backtest_task.apply_async(args=[strategy_name, strategy.to_dict(), start_date, end_date, money_amount, retry_number + 1], countdown=wait_time)
        else:
            raise Exception("Error creating backtest task! For some reason number of retries exceeded max permitted value.")

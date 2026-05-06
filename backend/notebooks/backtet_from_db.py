from datetime import datetime

from app.background_tasks.tasks.backtest import backtest_task
from app.backtest import backtest_service
from app.backtest.BacktestEngine import BacktestEngine
from app.strategies.implementation.RSIStrategy import RSIStrategy


strategy = RSIStrategy(timeframe="1h")

print(strategy.to_dict())

#start_date = datetime(2024, 12, 1, 0, 0)
#end_date = datetime(2025, 8, 2, 0, 0)

start_date = datetime(2024, 10, 1, 0, 0)
end_date = datetime(2025, 3, 1, 0, 0)

backtest_service.launch_backtest(strategy, start_date, end_date)
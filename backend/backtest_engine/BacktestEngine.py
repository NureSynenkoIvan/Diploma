from strategies.Strategy import Strategy
from backtest_engine.BacktestResult import BacktestResult

class BacktestEngine:
    def __init__(self):
        print("Backtest engine initialized")

    def run(self, strategy, historical_data, money_amount=0.0, money_symbol='USDT') -> BacktestResult:
        if (strategy.money_amount == 0.0):
            strategy.money_amount = money_amount
            strategy.money_symbol = money_symbol

        result = BacktestResult(strategy.name)

        # PLACEHOLDER
        # strategy.on_start()
        # for tick in historical_data:
        #     strategy.on_tick(tick)
        # strategy.on_stop()

        result.overall_profit_percent = 0.0
        result.mean_monthly_profit_percent = 0.0
        result.max_drawdown_percent = 0.0
        result.win_rate_percent = 0.0

        print("Backtest run completed")
        return result
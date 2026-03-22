from executor.Bot import Bot
from strategies.Strategy import Strategy
from backtest.BacktestResult import BacktestResult, Context
from executor.DataProvider import DataProvider

class BacktestEngine (DataProvider):
    def __init__(self):
        print("Backtest engine initialized")

    def run(self, strategy, historical_data, money_amount=0.0, money_symbol='USDT') -> BacktestResult:
        bot = Bot("name", strategy, historical_data, money_amount, money_symbol)
        
        print(f"Running backtest for strategy '{strategy.name}' with {len(historical_data)} ticks")
        print(f"Initial money: {money_amount} {money_symbol}")
        result = BacktestResult(strategy.name)

        self.execute_backtest(bot, historical_data)

        result.overall_profit_percent = 0.0
        result.mean_monthly_profit_percent = 0.0
        result.max_drawdown_percent = 0.0
        result.win_rate_percent = 0.0

        print("Backtest run completed")
        return result
    
    def execute_backtest(self, bot, historical_data):
        bot.on_start()
        
        for tick in historical_data:
            data = self.get_context(bot.strategy)

            bot.on_tick(data)

        bot.on_stop()

    def get_context(self, strategy) -> Context:
        """Build a Context for the given strategy's required symbols/timeframe."""
        # For simplicity, we return an empty context here. In a real implementation,
        # this would fetch market data and portfolio information relevant to the strategy.
        return Context(market_data=None, portfolio=None)
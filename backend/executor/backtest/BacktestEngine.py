from executor.Bot import Bot
from strategies.Strategy import Strategy
from backtest.BacktestResult import BacktestResult
from executor.Context import Context
from executor.portfolio.PortfolioProvider import BacktestPortfolioProvider
from executor.DataProvider import DataProvider

class BacktestEngine :
    def __init__(self):
        print("Backtest engine initialized")

    def run(self, strategy, historical_data, money_amount=0.0, money_symbol='USDT') -> BacktestResult:
        portfolio_provider = self.build_portfolio_provider(strategy)
        bot = Bot("name", strategy, historical_data, money_amount, money_symbol, regime='backtest', portfolio_provider=portfolio_provider)

        self.historical_data = historical_data
        
        
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
    
    def execute_backtest(self, bot : Bot, historical_data):
        bot.on_start()
        
        for tick in historical_data:
            data = self.get_market_data(bot.strategy)

            bot.on_tick(data)

        bot.on_stop()

    def get_context(self, strategy) -> Context:
        """Build a Context for the given strategy's required symbols/timeframe."""
        # this would fetch market data and portfolio information relevant to the strategy.
        strategy.validate_data_requirements(self.historical_data)
    
    def build_portfolio_provider(self, strategy):
        return BacktestPortfolioProvider(strategy)
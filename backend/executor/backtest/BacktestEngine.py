from backend.executor.execution.ExecutionEngine import BacktestExecutionEngine
from executor.Bot import Bot
from strategies.Strategy import Strategy
from backtest.BacktestResult import BacktestResult
from executor.Context import Context
from executor.portfolio.PortfolioProvider import BacktestPortfolioProvider
from backend.data.DataProvider import DataProvider, PandasBacktestDataProvider


class BacktestEngine :
    def __init__(self):
        print("Backtest engine initialized")

    def run(self, strategy : Strategy, historical_data_file, money_amount=0.0, money_symbol='USDT') -> BacktestResult:
        portfolio_provider = self.build_portfolio_provider(strategy)

        data_provider = self.load_historical_data(strategy, historical_data_file)

        bot = Bot(name="name", 
                  strategy=strategy, 
                  symbols=[],
                  execution_engine=BacktestExecutionEngine(), 
                  regime='backtest', 
                  portfolio_provider=portfolio_provider)
        
        
        print(f"Running backtest for strategy '{strategy.name}' w")
        print(f"Initial money: {money_amount} {money_symbol}")
        result = BacktestResult(strategy.name)

        self.execute_backtest(bot, data_provider)

        print("Backtest run completed")
        return result
    
    def execute_backtest(self, bot : Bot, data_provider : DataProvider) -> BacktestResult:
        bot.on_start()
        
        data = data_provider.get_market_data(bot.strategy)
        while data is not None:
            bot.on_tick(data)

            data = data_provider.get_market_data(bot.strategy)

        bot.on_stop()
        result = self.calculate_results(bot)
        return result


    def load_historical_data(self, strategy : Strategy, dataset_file) -> DataProvider:
        # Currently only supports CSV files, but can be extended to support other formats or data sources
        return PandasBacktestDataProvider(strategy, dataset_file)
    
    def build_portfolio_provider(self, strategy):
        return BacktestPortfolioProvider(strategy)
    
    def calculate_results(bot : Bot) -> BacktestResult:
        # This is a placeholder implementation. In a real implementation, this would calculate the backtest results
        # based on the final state of the portfolio and the historical data.
        pass

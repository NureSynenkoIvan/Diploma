
from backend.executor.execution.ExecutionEngine import ExecutionEngine
from backend.strategies.Strategy import Strategy
from executor.portfolio.PortfolioProvider import PortfolioProvider

from . import Context
class Bot:
    def __init__(self, 
                 name, 
                 strategy : Strategy, 
                 symbols=[], 
                 execution_engine : ExecutionEngine = None, 
                 regime='backtest', 
                 portfolio_provider=None):
        self.name=name
        self.strategy=strategy
        self.symbols = symbols
        self.execution_engine = execution_engine
        self.regime = regime
        self.portfolio_provider = portfolio_provider

        strategy.validate(self)

    async def on_tick(self, market_data):
        ctx = Context(market_data, self.portfolio_provider.get_portfolio())

        signals = self.strategy.on_tick(ctx)

        for signal in signals:
            order = signal.to_order()
            result = await self.execution_engine.execute(order)
            self.portfolio_provider.apply(order, result)

    async def on_start(self):
        ctx = Context(None, self.portfolio_provider.get_portfolio())
        await self.strategy.on_start(ctx)
    
    async def on_stop(self):
        ctx = Context(None, self.portfolio_provider.get_portfolio())
        await self.strategy.on_stop(ctx)
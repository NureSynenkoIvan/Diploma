from app.executor.execution.ExecutionEngine import ExecutionEngine
from app.strategies.Strategy import Strategy
from app.executor.Context import Context


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

        self.startingPosition

        strategy.validate(self)

    def on_tick(self, market_data):
        portfolio = self.portfolio_provider.get_portfolio(self)

        ctx = Context(market_data, portfolio)

        signals = self.strategy.on_tick(ctx)

        for signal in signals:
            order = signal.to_order()
            result = self.execution_engine.execute(order)
            if result.success:
                self.portfolio_provider.apply(order)

    def on_start(self, data=None):
        ctx = Context(data, self.portfolio_provider.get_portfolio(self))
        self.strategy.on_start(ctx)

    def on_stop(self, data=None):
        ctx = Context(data, self.portfolio_provider.get_portfolio(self))
        self.strategy.on_stop(ctx)

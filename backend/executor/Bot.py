from . import Context
class Bot:
    def __init__(self, name, strategy, symbols=[], execution_engine=None, portfolio=None):
        self.name=name
        self.strategy=strategy
        self.symbols = symbols
        self.execution_engine = execution_engine
        self.portfolio = portfolio

        strategy.validate(self)

    async def on_tick(self, market_data):
        ctx = Context(market_data, self.portfolio)

        signals = self.strategy.on_tick(ctx)

        for signal in signals:
            order = signal.to_order()
            result = await self.execution_engine.execute(order)
            self.portfolio.apply(result)

    async def on_start(self):
        ctx = Context(None, self.portfolio)
        await self.strategy.on_start(ctx)
    
    async def on_stop(self):
        ctx = Context(None, self.portfolio)
        await self.strategy.on_stop(ctx)
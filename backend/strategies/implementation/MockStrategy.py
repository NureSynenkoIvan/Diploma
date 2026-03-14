from strategies.Strategy import Strategy
from utils.Timeframe import Timeframe

class MockStrategy(Strategy):
    def __init__(self, name = "MockStrategy", description = "Mock strategy for testing", required_symbols = 1, timeframe = Timeframe.ONE_SECOND):
        super().__init__(name, description, required_symbols, timeframe)

    def on_tick(self, tick=0):
        print(f"{self.name}: Tick received: {tick}")
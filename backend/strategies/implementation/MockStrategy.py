from strategies.rules.strategy_requirements import MustHaveSufficientAmountOfSymbols
from strategies.Strategy import Strategy
from utils.Timeframe import Timeframe

class MockStrategy(Strategy):
    def __init__(self, name = "MockStrategy", description = "Mock strategy for testing", required_symbols = 4, timeframe = Timeframe.ONE_SECOND):
        super().__init__(name, description, required_symbols, timeframe)
        self.requirements.append(MustHaveSufficientAmountOfSymbols())

    def on_tick(self, tick=0):
        print(f"{self.name}: Tick received: {tick}\n")
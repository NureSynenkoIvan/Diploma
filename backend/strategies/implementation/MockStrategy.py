from strategies.rules.strategy_requirements import MustHaveSufficientAmountOfSymbols
from strategies.Strategy import Strategy
from utils.timeframe import Timeframe

class MockStrategy(Strategy):
    def __init__(self, name = "MockStrategy", description = "Mock strategy for testing"):
        super().__init__(name, description)
        self.requirements.append(MustHaveSufficientAmountOfSymbols())

    def on_tick(self, tick=0):
        print(f"{self.name}: Tick received: {tick}\n")
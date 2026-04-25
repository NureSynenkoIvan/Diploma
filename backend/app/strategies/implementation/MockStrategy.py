from app.strategies.rules.strategy_requirements import MustHaveSufficientAmountOfSymbols
from app.strategies.Strategy import Strategy


class MockStrategy(Strategy):
    def __init__(self, name = "MockStrategy", description = "Mock strategy for testing"):
        super().__init__(name, description)

    def on_tick(self, tick=0):
        print(f"{self.name}: Tick received: {tick}\n")
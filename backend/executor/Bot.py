class Bot:
    def __init__(self, name, strategy, symbols=[]):
        self.name=name
        self.strategy=strategy
        self.symbols = symbols
        self.validate(strategy)

    def validate(self, strategy):
        if (strategy.required_symbols != len(self.symbols)):
            raise Exception(f"Strategy requires {strategy.required_symbols} symbols, got only {len(self.symbols)}")

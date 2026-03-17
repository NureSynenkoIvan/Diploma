class Bot:
    def __init__(self, name, strategy, symbols=[]):
        self.name=name
        self.strategy=strategy
        self.symbols = symbols

        strategy.validate(self)

    

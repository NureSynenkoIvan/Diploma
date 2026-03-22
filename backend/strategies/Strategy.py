from utils.Timeframe import Timeframe
from executor.Context import Context

class Strategy:
    def __init__(self, name, description, required_symbols=[], timeframe=Timeframe.ONE_SECOND, money_amount=0.0, money_symbol='USDT'):
        self.name = name
        self.description = description
        self.required_symbols = required_symbols
        self.timeframe = timeframe
        self.money_amount = money_amount
        self.money_symbol = money_symbol
        self.requirements = []
        self.data_fetching_requirements = []

    def validate(self, bot):
        for requirement in self.requirements:
            requirement.validate(self, bot)

    def on_start(self):
        pass

    def on_tick(self, context : Context):
        pass
    
    def on_stop(self):
        pass
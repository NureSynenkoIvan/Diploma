from utils.Timeframe import Timeframe

class Strategy:
    def __init__(self, name, description, required_symbols = [], timeframe = Timeframe.ONE_SECOND):
        self.name = name
        self.description = description
        self.required_symbols = required_symbols
        self.timeframe = timeframe

    def on_start(self):
        pass

    def on_tick(self, tick=0):
        pass
    
    def on_order(self, order):
        pass
    
    def on_stop(self):
        pass
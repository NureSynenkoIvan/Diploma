
class Requirement:
    def validate(self, strategy, bot):
        pass

class MustHaveSufficientAmountOfSymbols(Requirement):
    def validate(self, strategy, bot):
        if (len(bot.symbols) < strategy.required_symbols):
            raise Exception(f"Strategy requires at least {strategy.required_symbols} symbols, got only {len(bot.symbols)}")
        
class DataRequirement(Requirement):
    def validate(self, data):
        pass

class MustBeCSVBinanceOHLCVData(DataRequirement):
    def validate(self, data):
        # This is a placeholder implementation. In a real implementation, this would check if the data
        # is in the correct format and contains the necessary fields for Binance OHLCV data.
        pass
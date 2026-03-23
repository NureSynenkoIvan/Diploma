import pandas as pd

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

class MustBePandasDataFrame(DataRequirement):
    def validate(self, data):
        if not isinstance(data, pd.DataFrame):
            raise Exception("Data must be a pandas DataFrame")

class MustBeBinanceOHLCVData(DataRequirement):
    def validate(self, data):
        required_columns = {'timestamp', 'open', 'high', 'low', 'close', 'volume'}
        if not required_columns.issubset(data.columns):
            raise Exception(f"Data must contain the following columns: {required_columns}")
        
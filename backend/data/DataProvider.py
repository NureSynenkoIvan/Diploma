
from strategies.Strategy import Strategy

import pandas as pd

class MarketDataProvider:
    def get_market_data(self, strategy):
        """Build a Context for the given strategy's required symbols/timeframe."""
        raise NotImplementedError("DataProvider is an abstract class. Implement get_context in a subclass.")

class PandasBacktestDataProvider(MarketDataProvider):
    def __init__(self, strategy : Strategy, historical_data_file):
        """Build a  for the given strategy's required symbols/timeframe."""
        self.historical_data = pd.read_csv(historical_data_file)
        strategy.validate_data_requirements(self.historical_data)

    def get_market_data(self, strategy : Strategy):
        #returns next row of historical data as a Context object
        if self.historical_data.empty:
            return None
        row = self.historical_data.iloc[0]
        self.historical_data = self.historical_data.iloc[1:]
        return row


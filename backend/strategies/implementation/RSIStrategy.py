

from backend.strategies.Strategy import Strategy

import talib

from backend.strategies.rules.strategy_requirements import DataRequirement, MustBePandasDataFrame, MustBeBinanceOHLCVData

class RSIStrategy(Strategy):
    def __init__(self, symbol, timeframe, rsi_period=14, overbought_threshold=70, oversold_threshold=30):
        super().__init__(symbol, timeframe)
        self.rsi_period = rsi_period
        self.overbought_threshold = overbought_threshold
        self.oversold_threshold = oversold_threshold
        self.data_requirements.append(MustBePandasDataFrame(), MustBeBinanceOHLCVData())
        self.data_window = []
    
    def on_tick(self, data):
        if len(self.data_window) < self.rsi_period:
            self.data_window.append(data)
            return []  # Not enough data to calculate RSI yet

        # Calculate RSI using the provided data and make trading decisions based on the thresholds
        close_prices = data['close']  # Assuming 'close' is a column in the data
        rsi = talib.RSI(close_prices, timeperiod=self.rsi_period)
        signals = []
        if rsi[-1] > self.overbought_threshold:
            signals.append('sell')
        elif rsi[-1] < self.oversold_threshold:
            signals.append('buy')

        self.data_window.pop(0)  # Remove the oldest data point to maintain the window size

        return signals
from collections import deque

from app.utils.timeframe import Timeframe
from app.executor import SimpleSignal
from app.strategies.Strategy import Strategy

import talib
import numpy as np

from app.strategies.rules.strategy_requirements import MustBePandasDataFrame, MustBeBinanceOHLCVData

class RSIStrategy(Strategy):
    """Default values were gotten from Backtests.ipynb"""
    def __init__(self, symbol="BTC/USDT", timeframe=Timeframe.ONE_MINUTE, rsi_period=8, overbought_threshold=62, oversold_threshold=36):
        super().__init__("RSIStrategy",
                         "Simple RSI strategy")
        self.required_symbols = [symbol]
        self.timeframe = timeframe
        self.rsi_period = rsi_period
        self.overbought_threshold = overbought_threshold
        self.oversold_threshold = oversold_threshold
        self.data_requirements = [MustBePandasDataFrame(), MustBeBinanceOHLCVData()]
        self.max_window = rsi_period + 50
        self.data_window = deque(maxlen=self.max_window)

    def on_tick(self, context):
        self.data_window.append(context.market_data['Close'])

        if len(self.data_window) < self.max_window:
            return []

        close_prices = np.fromiter(self.data_window, dtype=float)

        rsi_values = talib.RSI(close_prices, timeperiod=self.rsi_period)
        current_rsi = rsi_values[-1]

        if np.isnan(current_rsi):
            return []


        portfolio = context.portfolio
        last_close_price = close_prices[-1]
        if current_rsi > self.overbought_threshold and len(portfolio.positions) > 0:
            return [SimpleSignal(symbol=self.required_symbols[0],
                                 quantity=portfolio.positions[0].quantity,
                                 price=last_close_price,
                                 side="sell")]
        elif current_rsi < self.oversold_threshold and len(portfolio.positions) <= 0:
            target_asset_quantity = portfolio.base_token_amount / last_close_price
            return [SimpleSignal(symbol=self.required_symbols[0],
                                 quantity=target_asset_quantity,
                                 price=last_close_price,
                                 side="buy")]

        return []

class NPositionsRSIStrategy(RSIStrategy):
    """Regular RSI is better. See ..\\notebooks\\Backtests.ipynb"""
    def __init__(self, symbol="BTC/USDT", timeframe=Timeframe.ONE_MINUTE, rsi_period=8, overbought_threshold=70, oversold_threshold=35, max_positions=10):
        super().__init__(symbol, timeframe, rsi_period, overbought_threshold, oversold_threshold)
        self.name="1/N Positions RSI"
        self.max_positions = max_positions
        self.position_size=0

    def on_start(self, context):
        self.position_size = context.portfolio.base_token_amount / self.max_positions

    def on_tick(self, context):
        self.data_window.append(context.market_data['Close'])

        if len(self.data_window) < self.max_window:
            return []

        close_prices = np.fromiter(self.data_window, dtype=float)

        rsi_values = talib.RSI(close_prices, timeperiod=self.rsi_period)
        current_rsi = rsi_values[-1]

        if np.isnan(current_rsi):
            return []

        portfolio = context.portfolio
        last_close_price = close_prices[-1]
        if current_rsi > self.overbought_threshold and len(portfolio.positions) > 0:
            best_position = portfolio.positions[0]
            for position in portfolio.positions:
                if position.entry_price < best_position.entry_price:
                    best_position = position

            return [SimpleSignal(symbol=self.required_symbols[0],
                                 quantity=best_position.quantity,
                                 price=last_close_price,
                                 side="sell")]
        elif current_rsi < self.oversold_threshold and len(portfolio.positions) < self.max_positions:
            target_asset_quantity = self.position_size / last_close_price
            return [SimpleSignal(symbol=self.required_symbols[0],
                                 quantity=target_asset_quantity,
                                 price=last_close_price,
                                 side="buy")]

        return []

import unittest

from sqlalchemy import true

from strategies.implementation.RSIStrategy import RSIStrategy
import utils.Timeframe


class TestInspectStrategy(unittest.TestCase):


    def test_inspect_strategy(self):
        strategy = RSIStrategy(symbol="BTC/USCT", timeframe=utils.Timeframe.Timeframe.ONE_MINUTE, rsi_period=8, overbought_threshold=62, oversold_threshold=36)
        output = strategy.get_parameters_schema()
        assert(output is not None)
        assert (self.find_strategy_parameter_in_schema("rsi_period", output))
        assert (self.find_strategy_parameter_in_schema("overbought_threshold", output))
        assert (self.find_strategy_parameter_in_schema("oversold_threshold", output))

    def find_strategy_parameter_in_schema(self, parameter : str, output: list):
        for row in output:
            if row['key'] == parameter:
                return True
        return False

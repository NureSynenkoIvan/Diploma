
import time
from executor.Executor import Executor
from backend.executor import Context, DataProvider
from backend.strategies.Strategy import Strategy
import concurrent.futures
import os

class MultithreadExecutor(Executor):
    def __init__(self, bots = [], sleep_time = 1):
        super().__init__(bots, sleep_time)
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count())
        print(f"Initializing ThreadPoolExecutor with {os.cpu_count()} workers")
    
    def run(self):
        while True:
            for bot in self.get_bots_snapshot():   
                data = self.get_context(bot.strategy)             
                self.executor.submit(bot.strategy.on_tick(data), time.time())
            time.sleep(self.sleep_time)

    def get_context(self, strategy) -> Context:
        """Build a Context for the given strategy's required symbols/timeframe."""
        # For simplicity, we return an empty context here. In a real implementation,
        # this would fetch market data and portfolio information relevant to the strategy.
        return Context(market_data=None, portfolio=None)
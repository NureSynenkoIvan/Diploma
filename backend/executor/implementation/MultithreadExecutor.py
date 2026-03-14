
import time
from executor.Executor import Executor
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
                self.executor.submit(bot.strategy.on_tick, time.time())
            time.sleep(self.sleep_time)
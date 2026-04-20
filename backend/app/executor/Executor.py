from time import sleep
import threading
from app.executor.Bot import Bot

class Executor:
    def __init__(self, bots = list[Bot], sleep_time = 1):
        self.bots = bots
        self.sleep_time = sleep_time
        self._bots_lock = threading.Lock()

    def add_bot(self, bot):
        with self._bots_lock:
            self.bots.append(bot)
    
    def remove_bot(self, bot):
        with self._bots_lock:
            if bot in self.bots:
                self.bots.remove(bot)

    def get_bots_snapshot(self):
        with self._bots_lock:
            return list(self.bots)
    
    def start(self):
        for bot in self.get_bots_snapshot():
            bot.on_start()
    
    def stop(self):
        for bot in self.get_bots_snapshot():
            bot.on_stop()
    
    def run(self):
        while True:
            for bot in self.get_bots_snapshot():
                bot.on_tick()
            sleep(self.sleep_time)


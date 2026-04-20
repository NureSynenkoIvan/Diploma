from __future__ import annotations

import importlib
import inspect
import pkgutil
import threading
from dataclasses import dataclass

from db.models import Bot as BotModel
from db.models import Strategy as StrategyModel
from db.session import SessionLocal
from executor.Bot import Bot as RuntimeBot
from executor.implementation.MultithreadExecutor import MultithreadExecutor
from strategies.Strategy import Strategy as BaseStrategy


@dataclass
class RuntimeBotRecord:
    db_bot_id: int
    bot: RuntimeBot

class StrategyFactory:
    def __init__(self) -> None:
        self._classes_by_name: dict[str, type[BaseStrategy]] = {}
        self._loaded = False

    def _load(self) -> None:
        if self._loaded:
            return

        package_name = "strategies.implementation"
        package = importlib.import_module(package_name)

        for module_info in pkgutil.iter_modules(package.__path__):
            if module_info.ispkg:
                continue

            module = importlib.import_module(f"{package_name}.{module_info.name}")
            for _, obj in inspect.getmembers(module, inspect.isclass):
                if not issubclass(obj, BaseStrategy) or obj is BaseStrategy:
                    continue

                default_instance = obj()
                self._classes_by_name[default_instance.name] = obj
                self._classes_by_name[obj.__name__] = obj

        self._loaded = True

    def create(self, strategy_name: str) -> BaseStrategy:
        self._load()
        strategy_class = self._classes_by_name.get(strategy_name)
        if strategy_class is None:
            raise ValueError(f"No strategy implementation found for '{strategy_name}'")
        return strategy_class()


class BotRuntimeRegistry:
    def __init__(self, executor: MultithreadExecutor) -> None:
        self._executor = executor
        self._records: dict[int, RuntimeBotRecord] = {}
        self._lock = threading.Lock()
        self._strategy_factory = StrategyFactory()

    def start(self) -> None:
        self._executor.start()
        threading.Thread(target=self._executor.run, daemon=True).start()

    def load_existing_from_db(self) -> None:
        with SessionLocal() as db:
            bots = db.query(BotModel).all()
            for bot in bots:
                runtime_bot = self._build_runtime_bot(
                    bot.name, bot.symbols, bot.strategy,
                    bot.money_amount, bot.money_symbol,
                )
                self._add_runtime_bot(bot.id, runtime_bot)

    def create(self, db_bot_id: int, name: str, symbols: list[str], strategy: StrategyModel,
               money_amount: float | None = None, money_symbol: str | None = None) -> None:
        runtime_bot = self._build_runtime_bot(name, symbols, strategy, money_amount, money_symbol)
        self._add_runtime_bot(db_bot_id, runtime_bot)

    def update(self, db_bot_id: int, name: str, symbols: list[str], strategy: StrategyModel,
               money_amount: float | None = None, money_symbol: str | None = None) -> None:
        runtime_bot = self._build_runtime_bot(name, symbols, strategy, money_amount, money_symbol)
        with self._lock:
            previous = self._records.get(db_bot_id)
            if previous is not None:
                self._executor.remove_bot(previous.bot)
            self._executor.add_bot(runtime_bot)
            self._records[db_bot_id] = RuntimeBotRecord(db_bot_id=db_bot_id, bot=runtime_bot)

    def delete(self, db_bot_id: int) -> None:
        with self._lock:
            previous = self._records.pop(db_bot_id, None)
            if previous is not None:
                self._executor.remove_bot(previous.bot)

    def _build_runtime_bot(self, name: str, symbols: list[str], strategy: StrategyModel,
                           money_amount: float | None = None, money_symbol: str | None = None) -> RuntimeBot:
        runtime_strategy = self._strategy_factory.create(strategy.name)
        runtime_strategy.name = strategy.name
        runtime_strategy.description = strategy.description
        if money_amount is not None:
            runtime_strategy.money_amount = money_amount
        if money_symbol is not None:
            runtime_strategy.money_symbol = money_symbol
        return RuntimeBot(name=name, strategy=runtime_strategy, symbols=symbols)

    def _add_runtime_bot(self, db_bot_id: int, runtime_bot: RuntimeBot) -> None:
        with self._lock:
            self._executor.add_bot(runtime_bot)
            self._records[db_bot_id] = RuntimeBotRecord(db_bot_id=db_bot_id, bot=runtime_bot)

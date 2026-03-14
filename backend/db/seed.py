from __future__ import annotations

import importlib
import inspect
import pkgutil

from sqlalchemy import select

from api.auth import hash_password
from db.models import Strategy as StrategyModel, User
from db.session import db_session, init_db
from strategies.Strategy import Strategy as BaseStrategy

DEFAULT_LOGIN = "user"
DEFAULT_PASSWORD = "user"


def _iter_strategy_instances() -> list[BaseStrategy]:
    """Dynamically import strategy implementations and return instances of them.
    Modify the strategy in code and it'll persist in the database after running the seed function, without the need to modify the seed function itself.
    """
    strategy_instances: list[BaseStrategy] = []

    package_name = "strategies.implementation"
    package = importlib.import_module(package_name)

    for module_info in pkgutil.iter_modules(package.__path__):
        if module_info.ispkg:
            continue

        module = importlib.import_module(f"{package_name}.{module_info.name}")
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if not issubclass(obj, BaseStrategy) or obj is BaseStrategy:
                continue

            strategy_instances.append(obj())

    return strategy_instances


def _symbols_required(value: object) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, (list, tuple, set)):
        return len(value)
    return 1


def _timeframe_value(value: object) -> str:
    if hasattr(value, "name"):
        return str(value.name)
    return str(value)


def seed_defaults() -> None:
    """Create default records if they do not exist yet."""
    init_db()

    with db_session() as db:
        existing_user = db.execute(select(User).where(User.login == DEFAULT_LOGIN)).scalar_one_or_none()
        if existing_user is None:
            db.add(User(login=DEFAULT_LOGIN, password_hash=hash_password(DEFAULT_PASSWORD)))

        for strategy in _iter_strategy_instances():
            existing_strategy = (
                db.execute(select(StrategyModel).where(StrategyModel.name == strategy.name)).scalar_one_or_none()
            )
            if existing_strategy is not None:
                continue

            db.add(
                StrategyModel(
                    name=strategy.name,
                    description=strategy.description,
                    symbols_required=_symbols_required(strategy.required_symbols),
                    timeframe=_timeframe_value(strategy.timeframe),
                )
            )


if __name__ == "__main__":
    seed_defaults()

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


def _sqlite_url() -> str:
    return os.getenv("DATABASE_URL", "sqlite:///./app.db")


engine = create_engine(
    _sqlite_url(),
    connect_args={"check_same_thread": False},
)


class Base(DeclarativeBase):
    pass


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)


def init_db() -> None:
    # Import models so metadata is populated
    from db import models  # noqa: F401

    Base.metadata.create_all(bind=engine)

    # Keep SQLite schema in sync for environments without migrations.
    if engine.dialect.name == "sqlite":
        with engine.begin() as connection:
            columns = connection.execute(text("PRAGMA table_info(bots)"))
            column_names = {str(row[1]) for row in columns}
            if "additional_info" not in column_names:
                connection.execute(text("ALTER TABLE bots ADD COLUMN additional_info TEXT"))
            if "money_amount" not in column_names:
                connection.execute(text("ALTER TABLE bots ADD COLUMN money_amount REAL"))
            if "money_symbol" not in column_names:
                connection.execute(text("ALTER TABLE bots ADD COLUMN money_symbol TEXT"))


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def db_session() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

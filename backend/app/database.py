from __future__ import annotations

from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from .config import settings


connect_args = {}
if settings.database_url.startswith("sqlite"):
  connect_args = {"check_same_thread": False}

engine = create_engine(
  settings.database_url,
  connect_args=connect_args,
  future=True,
)

SessionLocal = sessionmaker(
  bind=engine,
  autoflush=False,
  autocommit=False,
  expire_on_commit=False,
  future=True,
)

Base = declarative_base()


def get_db() -> Iterator[Session]:
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()


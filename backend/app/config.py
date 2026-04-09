from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _default_database_url() -> str:
  root = Path(__file__).resolve().parents[2]
  data_dir = root / "data"
  data_dir.mkdir(parents=True, exist_ok=True)
  return f"sqlite:///{data_dir / 'dreams.db'}"


@dataclass(frozen=True)
class Settings:
  app_name: str
  database_url: str
  cors_origins: tuple[str, ...]


settings = Settings(
  app_name="Dream-as-a-Service",
  database_url=os.getenv("DREAM_DATABASE_URL", _default_database_url()),
  cors_origins=tuple(
    origin.strip()
    for origin in os.getenv(
      "DREAM_CORS_ORIGINS",
      "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173",
    ).split(",")
    if origin.strip()
  ),
)


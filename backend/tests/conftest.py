from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

TEST_DB_PATH = Path(__file__).parent / "test_dreams.db"
os.environ["DREAM_DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"
os.environ["DREAM_CORS_ORIGINS"] = "http://localhost:3000"

from app.database import Base, SessionLocal, engine
from app.main import app
from app.services.seed_data import seed_demo_data


@pytest.fixture()
def client() -> TestClient:
  Base.metadata.drop_all(bind=engine)
  Base.metadata.create_all(bind=engine)
  with SessionLocal() as session:
    seed_demo_data(session)
  with TestClient(app) as test_client:
    yield test_client

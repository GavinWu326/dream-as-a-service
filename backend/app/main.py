from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from .config import settings
from .database import Base, engine, get_db
from .models import DreamRun, Memory, Observation
from .schemas import (
  ConstellationPayload,
  DreamRunRead,
  MemoryRead,
  ObservationCreate,
  ObservationRead,
  OverviewRead,
  RetrieveContextRequest,
  RetrieveContextResponse,
  StoryRead,
)
from .services.dream_engine import build_constellation, build_overview, retrieve_context, run_dream, story_payload
from .services.seed_data import seed_demo_data


@asynccontextmanager
async def lifespan(_: FastAPI):
  Base.metadata.create_all(bind=engine)
  with Session(engine) as session:
    seed_demo_data(session)
  yield


app = FastAPI(
  title=settings.app_name,
  summary="A long-term memory service with an explicit dream phase.",
  version="0.1.0",
  lifespan=lifespan,
)

app.add_middleware(
  CORSMiddleware,
  allow_origins=list(settings.cors_origins),
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
  return {"status": "alive", "service": settings.app_name}


@app.get("/api/story", response_model=StoryRead)
def story() -> dict:
  return story_payload()


@app.get("/api/overview", response_model=OverviewRead)
def overview(db: Session = Depends(get_db)) -> dict:
  return build_overview(db)


@app.get("/api/observations", response_model=list[ObservationRead])
def list_observations(
  processed: Optional[bool] = Query(default=None),
  limit: int = Query(default=50, le=200),
  db: Session = Depends(get_db),
) -> list[Observation]:
  stmt = select(Observation).order_by(Observation.created_at.desc()).limit(limit)
  if processed is not None:
    stmt = stmt.where(Observation.processed.is_(processed))
  return db.scalars(stmt).all()


@app.post("/api/observations", response_model=ObservationRead, status_code=201)
def create_observation(payload: ObservationCreate, db: Session = Depends(get_db)) -> Observation:
  observation = Observation(**payload.model_dump())
  db.add(observation)
  db.commit()
  db.refresh(observation)
  return observation


@app.get("/api/memories", response_model=list[MemoryRead])
def list_memories(
  scope_type: Optional[str] = None,
  scope_id: Optional[str] = None,
  status: Optional[str] = None,
  limit: int = Query(default=30, le=200),
  db: Session = Depends(get_db),
) -> list[Memory]:
  stmt = select(Memory).order_by(Memory.strength.desc(), Memory.updated_at.desc()).limit(limit)
  if scope_type:
    stmt = stmt.where(Memory.scope_type == scope_type)
  if scope_id:
    stmt = stmt.where(Memory.scope_id == scope_id)
  if status:
    stmt = stmt.where(Memory.status == status)
  return db.scalars(stmt).all()


@app.get("/api/memories/{memory_id}", response_model=MemoryRead)
def get_memory(memory_id: int, db: Session = Depends(get_db)) -> Memory:
  memory = db.get(Memory, memory_id)
  if memory is None:
    raise HTTPException(status_code=404, detail="Memory not found")
  return memory


@app.post("/api/retrieve-context", response_model=RetrieveContextResponse)
def retrieve(payload: RetrieveContextRequest, db: Session = Depends(get_db)) -> dict:
  return retrieve_context(
    db,
    query=payload.query,
    scope_type=payload.scope_type,
    scope_id=payload.scope_id,
    limit=payload.limit,
  )


@app.get("/api/dream-runs", response_model=list[DreamRunRead])
def list_dream_runs(
  limit: int = Query(default=10, le=50),
  db: Session = Depends(get_db),
) -> list[DreamRun]:
  return db.scalars(
    select(DreamRun)
    .options(selectinload(DreamRun.mutations))
    .order_by(DreamRun.created_at.desc())
    .limit(limit)
  ).all()


@app.get("/api/dream-runs/{run_id}", response_model=DreamRunRead)
def get_dream_run(run_id: int, db: Session = Depends(get_db)) -> DreamRun:
  run = db.scalar(
    select(DreamRun)
    .options(selectinload(DreamRun.mutations))
    .where(DreamRun.id == run_id)
  )
  if run is None:
    raise HTTPException(status_code=404, detail="Dream run not found")
  return run


@app.post("/api/dream-runs", response_model=DreamRunRead, status_code=201)
def trigger_dream(db: Session = Depends(get_db)) -> DreamRun:
  return run_dream(db, mode="manual")


@app.get("/api/constellation", response_model=ConstellationPayload)
def constellation(db: Session = Depends(get_db)) -> dict:
  return build_constellation(db)

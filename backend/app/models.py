from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def utc_now() -> datetime:
  return datetime.utcnow()


class Observation(Base):
  __tablename__ = "observations"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
  source: Mapped[str] = mapped_column(String(64), default="chat")
  kind: Mapped[str] = mapped_column(String(64), default="project_signal")
  scope_type: Mapped[str] = mapped_column(String(32), index=True)
  scope_id: Mapped[str] = mapped_column(String(64), index=True)
  title: Mapped[str] = mapped_column(String(160))
  content: Mapped[str] = mapped_column(Text)
  importance: Mapped[float] = mapped_column(Float, default=0.6)
  confidence: Mapped[float] = mapped_column(Float, default=0.75)
  tags: Mapped[list[str]] = mapped_column(JSON, default=list)
  cluster_key: Mapped[Optional[str]] = mapped_column(String(96), index=True)
  type_hint: Mapped[Optional[str]] = mapped_column(String(24), index=True)
  processed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
  created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, index=True)


class Memory(Base):
  __tablename__ = "memories"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
  key: Mapped[str] = mapped_column(String(255), unique=True, index=True)
  memory_type: Mapped[str] = mapped_column(String(24), index=True)
  scope_type: Mapped[str] = mapped_column(String(32), index=True)
  scope_id: Mapped[str] = mapped_column(String(64), index=True)
  title: Mapped[str] = mapped_column(String(160))
  summary: Mapped[str] = mapped_column(Text)
  body: Mapped[str] = mapped_column(Text)
  status: Mapped[str] = mapped_column(String(24), default="active", index=True)
  freshness: Mapped[str] = mapped_column(String(24), default="alive", index=True)
  strength: Mapped[float] = mapped_column(Float, default=0.7)
  source_count: Mapped[int] = mapped_column(Integer, default=0)
  tags: Mapped[list[str]] = mapped_column(JSON, default=list)
  neuron_x: Mapped[float] = mapped_column(Float, default=50.0)
  neuron_y: Mapped[float] = mapped_column(Float, default=50.0)
  color: Mapped[str] = mapped_column(String(16), default="#79ffe1")
  last_dreamed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
  created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
  updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)

  mutations: Mapped[list["DreamMutation"]] = relationship(
    back_populates="memory",
    cascade="all, delete-orphan",
  )


class DreamRun(Base):
  __tablename__ = "dream_runs"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
  mode: Mapped[str] = mapped_column(String(24), default="incremental")
  status: Mapped[str] = mapped_column(String(24), default="completed", index=True)
  summary: Mapped[str] = mapped_column(Text)
  observations_seen: Mapped[int] = mapped_column(Integer, default=0)
  memories_created: Mapped[int] = mapped_column(Integer, default=0)
  memories_updated: Mapped[int] = mapped_column(Integer, default=0)
  memories_archived: Mapped[int] = mapped_column(Integer, default=0)
  created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
  completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

  mutations: Mapped[list["DreamMutation"]] = relationship(
    back_populates="dream_run",
    cascade="all, delete-orphan",
  )


class DreamMutation(Base):
  __tablename__ = "dream_mutations"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
  dream_run_id: Mapped[int] = mapped_column(ForeignKey("dream_runs.id"), index=True)
  memory_id: Mapped[Optional[int]] = mapped_column(ForeignKey("memories.id"), nullable=True)
  action: Mapped[str] = mapped_column(String(24))
  title: Mapped[str] = mapped_column(String(160))
  rationale: Mapped[str] = mapped_column(Text)
  before_state: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
  after_state: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

  dream_run: Mapped[DreamRun] = relationship(back_populates="mutations")
  memory: Mapped[Optional[Memory]] = relationship(back_populates="mutations")

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ObservationCreate(BaseModel):
  source: str = "chat"
  kind: str = "project_signal"
  scope_type: str
  scope_id: str
  title: str
  content: str
  importance: float = 0.6
  confidence: float = 0.75
  tags: list[str] = Field(default_factory=list)
  cluster_key: Optional[str] = None
  type_hint: Optional[str] = None


class ObservationRead(ObservationCreate):
  id: int
  processed: bool
  created_at: datetime

  model_config = ConfigDict(from_attributes=True)


class MemoryRead(BaseModel):
  id: int
  key: str
  memory_type: str
  scope_type: str
  scope_id: str
  title: str
  summary: str
  body: str
  status: str
  freshness: str
  strength: float
  source_count: int
  tags: list[str]
  neuron_x: float
  neuron_y: float
  color: str
  last_dreamed_at: Optional[datetime]
  created_at: datetime
  updated_at: datetime

  model_config = ConfigDict(from_attributes=True)


class DreamMutationRead(BaseModel):
  id: int
  action: str
  title: str
  rationale: str
  before_state: Optional[dict]
  after_state: Optional[dict]
  memory_id: Optional[int]

  model_config = ConfigDict(from_attributes=True)


class DreamRunRead(BaseModel):
  id: int
  mode: str
  status: str
  summary: str
  observations_seen: int
  memories_created: int
  memories_updated: int
  memories_archived: int
  created_at: datetime
  completed_at: Optional[datetime]
  mutations: list[DreamMutationRead] = Field(default_factory=list)

  model_config = ConfigDict(from_attributes=True)


class RetrievedMemory(BaseModel):
  memory: MemoryRead
  score: float
  reason: str


class RetrieveContextRequest(BaseModel):
  query: str
  scope_type: Optional[str] = None
  scope_id: Optional[str] = None
  limit: int = 5


class RetrieveContextResponse(BaseModel):
  query: str
  hits: list[RetrievedMemory]


class OverviewRead(BaseModel):
  observations_total: int
  observations_unprocessed: int
  memories_total: int
  active_memories: int
  dream_runs_total: int
  last_dream_summary: Optional[str]


class StoryRead(BaseModel):
  title: str
  premise: str
  principles: list[str]
  tagline: str


class ConstellationNode(BaseModel):
  id: str
  kind: str
  label: str
  x: float
  y: float
  radius: float
  color: str
  intensity: float
  meta: dict = Field(default_factory=dict)


class ConstellationEdge(BaseModel):
  source: str
  target: str
  weight: float
  glow: float
  relationship: str


class ConstellationPayload(BaseModel):
  nodes: list[ConstellationNode]
  edges: list[ConstellationEdge]
  latest_run_id: Optional[int]
  latest_run_summary: Optional[str]

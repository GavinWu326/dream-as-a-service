from __future__ import annotations

import math
import re
from collections import defaultdict
from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from ..models import DreamMutation, DreamRun, Memory, Observation


PALETTE = {
  "user": "#7ae7ff",
  "feedback": "#f5a9ff",
  "project": "#ffd36e",
  "reference": "#8dffbf",
}


def slugify(value: str) -> str:
  value = value.lower().strip()
  value = re.sub(r"[^a-z0-9]+", "-", value)
  return value.strip("-") or "memory"


def infer_memory_type(observation: Observation) -> str:
  if observation.type_hint in {"user", "feedback", "project", "reference"}:
    return observation.type_hint

  kind = observation.kind.lower()
  text = f"{observation.title} {observation.content}".lower()
  if "preference" in kind or "feedback" in kind or "avoid" in text:
    return "feedback"
  if "reference" in kind or "dashboard" in text or "linear" in text or "figma" in text:
    return "reference"
  if "profile" in kind or "goal" in kind or "role" in text or "prefers" in text:
    return "user"
  return "project"


def build_memory_key(
  scope_type: str,
  scope_id: str,
  memory_type: str,
  cluster_key: str,
) -> str:
  return f"{scope_type}:{scope_id}:{memory_type}:{cluster_key}"


def memory_position(key: str) -> tuple[float, float]:
  seed = sum(ord(char) * (index + 1) for index, char in enumerate(key))
  angle = (seed % 360) * math.pi / 180
  ring = 24 + (seed % 18)
  x = 50 + math.cos(angle) * ring
  y = 50 + math.sin(angle) * (ring * 0.72)
  return round(max(10, min(90, x)), 2), round(max(12, min(88, y)), 2)


def refresh_memory_freshness(memory: Memory) -> None:
  if memory.updated_at is None:
    memory.freshness = "alive"
    return

  age_days = max(0, (datetime.utcnow() - memory.updated_at).days)
  if age_days > 120:
    memory.freshness = "dormant"
  elif age_days > 45:
    memory.freshness = "fading"
  else:
    memory.freshness = "alive"


def synthesize_summary(memory_type: str, cluster_key: str, observations: list[Observation]) -> tuple[str, str, str]:
  title_lookup = {
    "feedback": "Collaboration Signal",
    "project": "Project Orbit",
    "reference": "Reference Beacon",
    "user": "User Portrait",
  }
  pretty_cluster = cluster_key.replace("-", " ").title()
  title = f"{title_lookup.get(memory_type, 'Memory')}: {pretty_cluster}"

  cues = []
  for observation in observations:
    if observation.title not in cues:
      cues.append(observation.title)

  summary = (
    f"{pretty_cluster} is now reinforced by {len(observations)} fresh signal"
    f"{'' if len(observations) == 1 else 's'}."
  )

  lines = ["Dream synthesis", ""]
  for observation in observations[:5]:
    lines.append(f"- {observation.content}")

  lines.extend(
    [
      "",
      "How to apply",
      "",
      f"- Treat this as a {memory_type} memory with real operational weight.",
      "- Re-verify if the surrounding system has materially changed.",
    ]
  )
  body = "\n".join(lines)
  return title, summary, body


def run_dream(session: Session, mode: str = "incremental") -> DreamRun:
  pending = session.scalars(
    select(Observation)
    .where(Observation.processed.is_(False))
    .order_by(Observation.created_at.asc())
  ).all()

  run = DreamRun(
    mode=mode,
    status="completed",
    summary="The dream found no new signal. The constellation stayed still.",
    observations_seen=len(pending),
    completed_at=datetime.utcnow(),
  )
  session.add(run)

  if not pending:
    session.commit()
    session.refresh(run)
    return run

  grouped: dict[tuple[str, str, str, str], list[Observation]] = defaultdict(list)
  for observation in pending:
    memory_type = infer_memory_type(observation)
    cluster_key = observation.cluster_key or slugify(observation.title)
    grouped[
      (
        observation.scope_type,
        observation.scope_id,
        memory_type,
        cluster_key,
      )
    ].append(observation)

  created = 0
  updated = 0
  archived = 0

  for (scope_type, scope_id, memory_type, cluster_key), observations in grouped.items():
    key = build_memory_key(scope_type, scope_id, memory_type, cluster_key)
    memory = session.scalar(select(Memory).where(Memory.key == key))
    title, summary, body = synthesize_summary(memory_type, cluster_key, observations)
    tags = sorted({tag for observation in observations for tag in observation.tags} | {cluster_key})

    if memory is None:
      neuron_x, neuron_y = memory_position(key)
      memory = Memory(
        key=key,
        memory_type=memory_type,
        scope_type=scope_type,
        scope_id=scope_id,
        title=title,
        summary=summary,
        body=body,
        tags=tags,
        strength=min(0.98, 0.58 + (len(observations) * 0.07)),
        source_count=len(observations),
        color=PALETTE.get(memory_type, "#7ae7ff"),
        neuron_x=neuron_x,
        neuron_y=neuron_y,
        last_dreamed_at=datetime.utcnow(),
      )
      refresh_memory_freshness(memory)
      session.add(memory)
      session.flush()
      run.mutations.append(
        DreamMutation(
          action="create",
          title=memory.title,
          rationale=f"Cluster `{cluster_key}` surfaced as a new durable {memory_type} memory.",
          before_state=None,
          after_state={
            "summary": memory.summary,
            "strength": memory.strength,
            "source_count": memory.source_count,
          },
          memory=memory,
        )
      )
      created += 1
    else:
      before_state = {
        "summary": memory.summary,
        "strength": memory.strength,
        "source_count": memory.source_count,
      }
      memory.title = title
      memory.summary = summary
      memory.body = body
      memory.tags = sorted(set(memory.tags or []).union(tags))
      memory.source_count += len(observations)
      memory.strength = min(0.99, memory.strength + (len(observations) * 0.035))
      memory.last_dreamed_at = datetime.utcnow()
      memory.updated_at = datetime.utcnow()
      refresh_memory_freshness(memory)
      run.mutations.append(
        DreamMutation(
          action="update",
          title=memory.title,
          rationale=f"Cluster `{cluster_key}` reinforced an existing memory with fresher signal.",
          before_state=before_state,
          after_state={
            "summary": memory.summary,
            "strength": memory.strength,
            "source_count": memory.source_count,
          },
          memory=memory,
        )
      )
      updated += 1

    for observation in observations:
      observation.processed = True

  stale_memories = session.scalars(select(Memory).where(Memory.status == "active")).all()
  for memory in stale_memories:
    refresh_memory_freshness(memory)
    if memory.freshness == "dormant" and memory.strength < 0.45:
      memory.status = "archived"
      archived += 1
      run.mutations.append(
        DreamMutation(
          action="archive",
          title=memory.title,
          rationale="Weak and dormant memory archived to keep the constellation legible.",
          before_state={"status": "active"},
          after_state={"status": "archived"},
          memory=memory,
        )
      )

  run.memories_created = created
  run.memories_updated = updated
  run.memories_archived = archived
  run.summary = (
    f"The dream touched {len(grouped)} memory clusters, created {created}, "
    f"updated {updated}, and archived {archived}."
  )

  session.commit()
  session.refresh(run)
  return session.scalar(
    select(DreamRun)
    .options(selectinload(DreamRun.mutations))
    .where(DreamRun.id == run.id)
  )


def build_overview(session: Session) -> dict:
  observations_total = session.scalar(select(func.count()).select_from(Observation)) or 0
  observations_unprocessed = session.scalar(
    select(func.count()).select_from(Observation).where(Observation.processed.is_(False))
  ) or 0
  memories_total = session.scalar(select(func.count()).select_from(Memory)) or 0
  active_memories = session.scalar(
    select(func.count()).select_from(Memory).where(Memory.status == "active")
  ) or 0
  dream_runs_total = session.scalar(select(func.count()).select_from(DreamRun)) or 0
  latest_run = session.scalar(select(DreamRun).order_by(DreamRun.created_at.desc()).limit(1))

  return {
    "observations_total": observations_total,
    "observations_unprocessed": observations_unprocessed,
    "memories_total": memories_total,
    "active_memories": active_memories,
    "dream_runs_total": dream_runs_total,
    "last_dream_summary": latest_run.summary if latest_run else None,
  }


def tokenize(value: str) -> list[str]:
  return [token for token in re.findall(r"[a-z0-9]+", value.lower()) if len(token) > 1]


def retrieve_context(
  session: Session,
  query: str,
  scope_type: Optional[str],
  scope_id: Optional[str],
  limit: int,
) -> dict:
  stmt = select(Memory).where(Memory.status == "active")
  if scope_type:
    stmt = stmt.where(Memory.scope_type == scope_type)
  if scope_id:
    stmt = stmt.where(Memory.scope_id == scope_id)

  tokens = tokenize(query)
  hits = []

  for memory in session.scalars(stmt).all():
    haystack = " ".join(
      [
        memory.title.lower(),
        memory.summary.lower(),
        memory.body.lower(),
        " ".join(memory.tags or []).lower(),
      ]
    )
    overlap = sum(1 for token in tokens if token in haystack)
    freshness_bonus = {"alive": 0.25, "fading": 0.1, "dormant": -0.15}.get(memory.freshness, 0)
    scope_bonus = 0.25 if scope_type and scope_type == memory.scope_type else 0
    score = overlap * 1.8 + memory.strength + freshness_bonus + scope_bonus
    if overlap == 0 and tokens:
      continue
    hits.append(
      {
        "memory": memory,
        "score": round(score, 3),
        "reason": (
          f"Matched {overlap} query cue(s), {memory.freshness} freshness, "
          f"strength {memory.strength:.2f}."
        ),
      }
    )

  hits.sort(key=lambda item: item["score"], reverse=True)
  return {"query": query, "hits": hits[:limit]}


def build_constellation(session: Session) -> dict:
  memories = session.scalars(
    select(Memory)
    .where(Memory.status != "archived")
    .order_by(Memory.strength.desc(), Memory.updated_at.desc())
    .limit(16)
  ).all()
  latest_runs = session.scalars(
    select(DreamRun)
    .options(selectinload(DreamRun.mutations))
    .order_by(DreamRun.created_at.desc())
    .limit(3)
  ).all()
  recent_observations = session.scalars(
    select(Observation).order_by(Observation.created_at.desc()).limit(18)
  ).all()

  memory_by_key = {memory.key: memory for memory in memories}
  nodes = []
  edges = []

  for memory in memories:
    nodes.append(
      {
        "id": f"memory-{memory.id}",
        "kind": "memory",
        "label": memory.title,
        "x": memory.neuron_x,
        "y": memory.neuron_y,
        "radius": 8 + (memory.strength * 10),
        "color": memory.color,
        "intensity": memory.strength,
        "meta": {
          "type": memory.memory_type,
          "freshness": memory.freshness,
          "summary": memory.summary,
          "scope": f"{memory.scope_type}:{memory.scope_id}",
        },
      }
    )

  for index, run in enumerate(reversed(latest_runs), start=1):
    nodes.append(
      {
        "id": f"dream-{run.id}",
        "kind": "dream",
        "label": f"Dream #{run.id}",
        "x": 16 + (index * 18),
        "y": 16 + (index * 8),
        "radius": 7 + len(run.mutations) * 0.3,
        "color": "#ffb86b",
        "intensity": 0.85,
        "meta": {"summary": run.summary, "mutations": len(run.mutations)},
      }
    )
    for mutation in run.mutations:
      if mutation.memory_id is None:
        continue
      edges.append(
        {
          "source": f"dream-{run.id}",
          "target": f"memory-{mutation.memory_id}",
          "weight": 0.55 if mutation.action == "update" else 0.85,
          "glow": 0.9,
          "relationship": mutation.action,
        }
      )

  for index, observation in enumerate(recent_observations):
    memory_type = infer_memory_type(observation)
    cluster_key = observation.cluster_key or slugify(observation.title)
    key = build_memory_key(observation.scope_type, observation.scope_id, memory_type, cluster_key)
    anchor = memory_by_key.get(key)
    if anchor is None:
      anchor_x, anchor_y = memory_position(key)
    else:
      anchor_x, anchor_y = anchor.neuron_x, anchor.neuron_y

    angle = (index * 37) * math.pi / 180
    x = anchor_x + math.cos(angle) * 7.5
    y = anchor_y + math.sin(angle) * 5.5
    nodes.append(
      {
        "id": f"observation-{observation.id}",
        "kind": "observation",
        "label": observation.title,
        "x": round(max(6, min(94, x)), 2),
        "y": round(max(8, min(92, y)), 2),
        "radius": 3.8 + (observation.importance * 3.6),
        "color": "#c6d3ff" if observation.processed else "#ffffff",
        "intensity": observation.confidence,
        "meta": {
          "processed": observation.processed,
          "kind": observation.kind,
          "scope": f"{observation.scope_type}:{observation.scope_id}",
        },
      }
    )

    if anchor is not None:
      edges.append(
        {
          "source": f"observation-{observation.id}",
          "target": f"memory-{anchor.id}",
          "weight": 0.35 + observation.importance * 0.35,
          "glow": 0.4 if observation.processed else 0.75,
          "relationship": "feeds",
        }
      )

  latest_run = latest_runs[0] if latest_runs else None
  return {
    "nodes": nodes,
    "edges": edges,
    "latest_run_id": latest_run.id if latest_run else None,
    "latest_run_summary": latest_run.summary if latest_run else None,
  }


def story_payload() -> dict:
  return {
    "title": "Dream-as-a-Service",
    "tagline": "A night-shift memory engine for agents that should remember with taste.",
    "premise": (
      "Agents spend the day collecting sparks. The dream service wakes later, "
      "sorts signal from noise, and leaves behind a constellation instead of a log pile."
    ),
    "principles": [
      "Observations are raw weather. Memories are shaped climate.",
      "A dream should merge, prune, and correct, not just summarize.",
      "Recall must privilege relevance and freshness over sheer volume.",
      "Good long-term memory is governed, not merely stored.",
    ],
  }

# Dream-as-a-Service

> By day, your agents collect sparks.  
> By night, this service turns them into constellations.

Dream-as-a-Service is a small but complete reference implementation of a **long-term memory lifecycle service** for AI agents.

It is not a chat transcript archive.  
It is not a vector store with nicer branding.  
It is a system for **observations, consolidation, durable memory, and recall**.

The central idea is simple:

- agents gather raw observations while they work
- a background or manual **dream run** revisits those observations
- the dream merges signal, prunes noise, updates durable memories, and leaves behind a cleaner graph for future recall

This repository ships as a full-stack demo with:

- a `FastAPI` backend
- a dreamy frontend visualization inspired by neuron clusters and celestial maps
- rich default seed data
- API tests
- Dockerfiles for both services
- a `docker-compose.yml` for one-command local launch

## The Premise

Most agent memory systems fail in a predictable way: they become hoarders.

They remember too much.  
They remember without taste.  
They retrieve stale fragments with the confidence of prophecy.

Dream-as-a-Service tries a different posture:

1. **Observations are cheap.**
   Let agents record raw signals freely.

2. **Durable memory is expensive.**
   Only promote what remains useful beyond the current turn.

3. **Dreams are the governance layer.**
   A dream is not another save. It is a reflective pass that can create, update, merge, or archive memory.

4. **Recall should feel curated.**
   The future agent should inherit a memory constellation, not a junk drawer.

## What Exists In This Demo

### Backend

The backend models four core entities:

- `Observation`
- `Memory`
- `DreamRun`
- `DreamMutation`

Key endpoints:

- `GET /api/health`
- `GET /api/story`
- `GET /api/overview`
- `GET /api/observations`
- `POST /api/observations`
- `GET /api/memories`
- `GET /api/memories/{id}`
- `POST /api/retrieve-context`
- `GET /api/dream-runs`
- `GET /api/dream-runs/{id}`
- `POST /api/dream-runs`
- `GET /api/constellation`

### Frontend

The frontend is intentionally not a generic admin dashboard.

It presents the service as a **nocturnal memory observatory**:

- a poster-like first viewport
- a neuron-and-starlight graph for observations, memories, and dream runs
- a latest-dream rail
- durable memory ribbons
- incoming signal weather

### Seed Data

The demo includes a fictional but realistic operating world:

- distinct users with collaboration preferences
- project constraints
- team-level references
- unprocessed observations waiting for the next dream

This gives the UI something alive to render on first boot and makes the API useful immediately.

## Memory Model

This implementation uses four durable memory types:

- `user`
- `feedback`
- `project`
- `reference`

That choice is deliberate.  
The service is trying to preserve **non-obvious future context**, not mirror code, tickets, or documentation line-for-line.

## How A Dream Works

In this repository, a dream run does the following:

1. Reads all unprocessed observations.
2. Groups them into memory clusters using scope, type, and cluster key.
3. Creates new memories or updates existing ones.
4. Refreshes freshness state.
5. Optionally archives weak dormant memories.
6. Records every mutation in a `DreamRun`.

You can think of it as:

`observation stream -> dream consolidation -> durable memory graph -> recall`

## Local Development

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend will start on `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend will start on `http://localhost:5173`.

If you want the frontend to point to a custom backend:

```bash
VITE_API_BASE_URL=http://localhost:8000/api npm run dev
```

## Docker

Run the full experience with:

```bash
docker compose up --build
```

Then open:

- frontend: `http://localhost:3000`
- backend API: `http://localhost:8000`

The frontend container proxies `/api` to the backend automatically.

## Tests

```bash
cd backend
pytest
```

The tests verify:

- seed data appears on startup
- context retrieval returns relevant memories
- manual dream runs process pending observations
- the constellation payload includes memories, observations, and dreams
- new observations can be created through the API

## Why This Project Exists

This repo is meant to be a **first version of a product idea**, not just a coding exercise.

If you want to turn Dream-as-a-Service into a real platform, the next layers would be:

- multi-tenant auth
- memory policies
- human review for dream mutations
- stronger retrieval ranking
- workflow integrations
- background scheduling
- audit views and memory lineage

## Art Direction

The interface is built around a visual thesis:

> memory should feel less like a filing cabinet and more like a living night sky

That is why the project uses:

- deep-ocean and amber tones
- poster-scale typography
- sparse composition
- animated graph pulses instead of dashboard tiles

The goal is not novelty for novelty's sake.  
It is to make the system's behavior legible through atmosphere.

## Repository Structure

```text
dream-as-a-service
├── backend
│   ├── app
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── services
│   ├── tests
│   └── Dockerfile
├── frontend
│   ├── src
│   │   ├── components
│   │   ├── lib
│   │   └── styles.css
│   └── Dockerfile
└── docker-compose.yml
```

## Final Note

A good memory system should not only ask:

**What can we store?**

It should ask:

**What deserves to survive the night?**

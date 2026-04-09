from __future__ import annotations


def test_seeded_overview_has_data(client):
  response = client.get("/api/overview")
  payload = response.json()

  assert response.status_code == 200
  assert payload["observations_total"] >= 18
  assert payload["memories_total"] >= 8
  assert payload["observations_unprocessed"] >= 1


def test_retrieve_context_returns_ranked_hits(client):
  response = client.post(
    "/api/retrieve-context",
    json={"query": "latency grafana oncall", "scope_type": "team", "scope_id": "team_nocturne"},
  )
  payload = response.json()

  assert response.status_code == 200
  assert payload["hits"]
  assert "latency" in payload["hits"][0]["memory"]["summary"].lower()


def test_trigger_dream_processes_pending_observations(client):
  before = client.get("/api/overview").json()
  response = client.post("/api/dream-runs")
  after = client.get("/api/overview").json()

  assert response.status_code == 201
  assert response.json()["observations_seen"] >= 1
  assert response.json()["memories_created"] + response.json()["memories_updated"] >= 1
  assert after["observations_unprocessed"] < before["observations_unprocessed"]


def test_constellation_contains_multiple_kinds_of_nodes(client):
  client.post("/api/dream-runs")
  response = client.get("/api/constellation")
  payload = response.json()

  kinds = {node["kind"] for node in payload["nodes"]}

  assert response.status_code == 200
  assert {"memory", "observation", "dream"}.issubset(kinds)
  assert payload["edges"]


def test_create_observation_adds_new_signal(client):
  response = client.post(
    "/api/observations",
    json={
      "scope_type": "project",
      "scope_id": "p_lighthouse",
      "kind": "project_signal",
      "title": "A new lighthouse pulse",
      "content": "Operators now annotate fragile workflows before handoff.",
      "cluster_key": "fragile-workflow-handoff",
      "type_hint": "project",
      "tags": ["handoff", "workflow"],
    },
  )

  assert response.status_code == 201
  assert response.json()["processed"] is False


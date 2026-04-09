import type {
  ConstellationPayload,
  DreamRun,
  Memory,
  Observation,
  Overview,
  Story,
} from "./types";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";

async function readJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
    },
    ...init,
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function fetchStory() {
  return readJson<Story>("/story");
}

export function fetchOverview() {
  return readJson<Overview>("/overview");
}

export function fetchMemories() {
  return readJson<Memory[]>("/memories?limit=18");
}

export function fetchDreamRuns() {
  return readJson<DreamRun[]>("/dream-runs?limit=6");
}

export function fetchObservations() {
  return readJson<Observation[]>("/observations?limit=18");
}

export function fetchConstellation() {
  return readJson<ConstellationPayload>("/constellation");
}

export function triggerDream() {
  return readJson<DreamRun>("/dream-runs", { method: "POST" });
}


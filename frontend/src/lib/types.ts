export type Story = {
  title: string;
  tagline: string;
  premise: string;
  principles: string[];
};

export type Overview = {
  observations_total: number;
  observations_unprocessed: number;
  memories_total: number;
  active_memories: number;
  dream_runs_total: number;
  last_dream_summary: string | null;
};

export type Memory = {
  id: number;
  key: string;
  memory_type: string;
  scope_type: string;
  scope_id: string;
  title: string;
  summary: string;
  body: string;
  status: string;
  freshness: string;
  strength: number;
  source_count: number;
  tags: string[];
  neuron_x: number;
  neuron_y: number;
  color: string;
  last_dreamed_at: string | null;
  created_at: string;
  updated_at: string;
};

export type DreamMutation = {
  id: number;
  action: string;
  title: string;
  rationale: string;
  before_state: Record<string, unknown> | null;
  after_state: Record<string, unknown> | null;
  memory_id: number | null;
};

export type DreamRun = {
  id: number;
  mode: string;
  status: string;
  summary: string;
  observations_seen: number;
  memories_created: number;
  memories_updated: number;
  memories_archived: number;
  created_at: string;
  completed_at: string | null;
  mutations: DreamMutation[];
};

export type Observation = {
  id: number;
  source: string;
  kind: string;
  scope_type: string;
  scope_id: string;
  title: string;
  content: string;
  importance: number;
  confidence: number;
  tags: string[];
  cluster_key: string | null;
  type_hint: string | null;
  processed: boolean;
  created_at: string;
};

export type ConstellationNode = {
  id: string;
  kind: "memory" | "observation" | "dream";
  label: string;
  x: number;
  y: number;
  radius: number;
  color: string;
  intensity: number;
  meta: Record<string, unknown>;
};

export type ConstellationEdge = {
  source: string;
  target: string;
  weight: number;
  glow: number;
  relationship: string;
};

export type ConstellationPayload = {
  nodes: ConstellationNode[];
  edges: ConstellationEdge[];
  latest_run_id: number | null;
  latest_run_summary: string | null;
};


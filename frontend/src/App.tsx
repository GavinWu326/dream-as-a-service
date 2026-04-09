import { startTransition, useEffect, useState } from "react";
import { motion } from "framer-motion";

import { NeuralConstellation } from "./components/NeuralConstellation";
import {
  fetchConstellation,
  fetchDreamRuns,
  fetchMemories,
  fetchObservations,
  fetchOverview,
  fetchStory,
  triggerDream,
} from "./lib/api";
import type { ConstellationPayload, DreamRun, Memory, Observation, Overview, Story } from "./lib/types";

type DashboardState = {
  story: Story | null;
  overview: Overview | null;
  memories: Memory[];
  dreamRuns: DreamRun[];
  observations: Observation[];
  constellation: ConstellationPayload | null;
};

const emptyState: DashboardState = {
  story: null,
  overview: null,
  memories: [],
  dreamRuns: [],
  observations: [],
  constellation: null,
};

export default function App() {
  const [state, setState] = useState<DashboardState>(emptyState);
  const [loading, setLoading] = useState(true);
  const [dreaming, setDreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void hydrate();
  }, []);

  async function hydrate() {
    try {
      setLoading(true);
      const [story, overview, memories, dreamRuns, observations, constellation] = await Promise.all([
        fetchStory(),
        fetchOverview(),
        fetchMemories(),
        fetchDreamRuns(),
        fetchObservations(),
        fetchConstellation(),
      ]);

      startTransition(() => {
        setState({ story, overview, memories, dreamRuns, observations, constellation });
        setError(null);
      });
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unknown loading error");
    } finally {
      setLoading(false);
    }
  }

  async function handleDream() {
    try {
      setDreaming(true);
      await triggerDream();
      await hydrate();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Dream failed");
    } finally {
      setDreaming(false);
    }
  }

  const latestRun = state.dreamRuns[0] ?? null;
  const heroStory = state.story;

  return (
    <div className="page-shell">
      <div className="backdrop-orbit backdrop-a" />
      <div className="backdrop-orbit backdrop-b" />

      <header className="hero">
        <div className="hero-copy">
          <p className="eyebrow">{heroStory?.title ?? "Dream-as-a-Service"}</p>
          <h1>{heroStory?.tagline ?? "A night-shift memory engine for agents."}</h1>
          <p className="lede">
            {heroStory?.premise ??
              "The daytime system gathers fragments. The night shift turns them into something future sessions can actually use."}
          </p>

          <div className="hero-actions">
            <button className="primary-button" onClick={handleDream} disabled={dreaming}>
              {dreaming ? "Dreaming..." : "Trigger a dream run"}
            </button>
            <span className="hero-note">
              {state.overview
                ? `${state.overview.observations_unprocessed} fresh signals waiting in the dark`
                : "Loading the constellation"}
            </span>
          </div>
        </div>

        <motion.div
          className="hero-poster"
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1.1, ease: "easeOut" }}
        >
          <div className="poster-surface">
            <span className="poster-label">Nocturnal Memory Lifecycle</span>
            <div className="poster-stages">
              <div>Observation</div>
              <div>Dream</div>
              <div>Memory</div>
              <div>Recall</div>
            </div>
          </div>
        </motion.div>
      </header>

      <main className="main-grid">
        <section className="constellation-panel">
          <NeuralConstellation constellation={state.constellation} />
        </section>

        <section className="status-rail">
          <div className="rail-block">
            <p className="eyebrow">Metrics</p>
            <div className="metric-list">
              <div>
                <strong>{state.overview?.memories_total ?? "..."}</strong>
                <span>memories</span>
              </div>
              <div>
                <strong>{state.overview?.observations_total ?? "..."}</strong>
                <span>observations</span>
              </div>
              <div>
                <strong>{state.overview?.dream_runs_total ?? "..."}</strong>
                <span>dreams</span>
              </div>
            </div>
          </div>

          <div className="rail-block">
            <p className="eyebrow">Latest dream</p>
            <h3>{latestRun ? `Dream #${latestRun.id}` : "Still gathering"}</h3>
            <p>{latestRun?.summary ?? "No dream has crossed the graph yet."}</p>
            <ul className="mutation-list">
              {(latestRun?.mutations ?? []).slice(0, 5).map((mutation) => (
                <li key={mutation.id}>
                  <span>{mutation.action}</span>
                  <strong>{mutation.title}</strong>
                </li>
              ))}
            </ul>
          </div>

          <div className="rail-block">
            <p className="eyebrow">Principles</p>
            <ul className="principle-list">
              {(heroStory?.principles ?? []).map((principle) => (
                <li key={principle}>{principle}</li>
              ))}
            </ul>
          </div>
        </section>

        <section className="memory-gallery">
          <div className="section-head">
            <p className="eyebrow">Durable memories</p>
            <h2>What survived the night</h2>
          </div>
          <div className="memory-stream">
            {state.memories.slice(0, 8).map((memory) => (
              <article key={memory.id} className="memory-ribbon">
                <span className="memory-type" style={{ backgroundColor: memory.color }} />
                <div>
                  <p className="memory-kicker">
                    {memory.memory_type} · {memory.scope_type}:{memory.scope_id}
                  </p>
                  <h3>{memory.title}</h3>
                  <p>{memory.summary}</p>
                  <div className="memory-meta">
                    <span>{memory.freshness}</span>
                    <span>{memory.source_count} signals</span>
                    <span>{Math.round(memory.strength * 100)}% strength</span>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="observation-band">
          <div className="section-head">
            <p className="eyebrow">Incoming weather</p>
            <h2>Raw signals still waiting</h2>
          </div>
          <div className="observation-list">
            {state.observations.slice(0, 7).map((observation) => (
              <article key={observation.id} className={`observation-chip ${observation.processed ? "settled" : "pending"}`}>
                <p>{observation.title}</p>
                <span>
                  {observation.processed ? "already absorbed" : "still bright"} · {observation.scope_type}:{observation.scope_id}
                </span>
              </article>
            ))}
          </div>
        </section>
      </main>

      {error ? <div className="error-banner">{error}</div> : null}
      {loading ? <div className="loading-banner">Tuning the telescope...</div> : null}
    </div>
  );
}


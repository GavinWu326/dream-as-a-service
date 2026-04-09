import { motion } from "framer-motion";

import type { ConstellationPayload } from "../lib/types";

type Props = {
  constellation: ConstellationPayload | null;
};

export function NeuralConstellation({ constellation }: Props) {
  if (!constellation) {
    return <div className="constellation-shell skeleton" />;
  }

  const nodeMap = new Map(constellation.nodes.map((node) => [node.id, node]));

  return (
    <div className="constellation-shell">
      <svg viewBox="0 0 100 100" className="constellation-svg" preserveAspectRatio="none">
        <defs>
          <radialGradient id="nodeGlow" cx="50%" cy="50%" r="65%">
            <stop offset="0%" stopColor="rgba(255,255,255,0.95)" />
            <stop offset="100%" stopColor="rgba(255,255,255,0)" />
          </radialGradient>
          <linearGradient id="edgeFlow" x1="0%" x2="100%" y1="0%" y2="0%">
            <stop offset="0%" stopColor="rgba(115,213,255,0.08)" />
            <stop offset="50%" stopColor="rgba(255,210,122,0.65)" />
            <stop offset="100%" stopColor="rgba(115,213,255,0.08)" />
          </linearGradient>
        </defs>

        {constellation.edges.map((edge) => {
          const source = nodeMap.get(edge.source);
          const target = nodeMap.get(edge.target);
          if (!source || !target) {
            return null;
          }

          return (
            <motion.line
              key={`${edge.source}-${edge.target}`}
              x1={source.x}
              y1={source.y}
              x2={target.x}
              y2={target.y}
              stroke="url(#edgeFlow)"
              strokeWidth={0.1 + edge.weight * 0.24}
              strokeOpacity={0.2 + edge.glow * 0.55}
              initial={{ pathLength: 0, opacity: 0 }}
              animate={{ pathLength: 1, opacity: 1 }}
              transition={{ duration: 1.6, ease: "easeOut" }}
            />
          );
        })}

        {constellation.nodes.map((node) => (
          <g key={node.id}>
            <circle
              cx={node.x}
              cy={node.y}
              r={node.radius * 1.75}
              fill="url(#nodeGlow)"
              opacity={0.12 + node.intensity * 0.16}
            />
            <motion.circle
              cx={node.x}
              cy={node.y}
              r={node.radius}
              fill={node.color}
              initial={{ scale: 0.9, opacity: 0.15 }}
              animate={{ scale: [1, 1.05, 1], opacity: [0.55, 1, 0.7] }}
              transition={{
                duration: 3.5 - Math.min(node.intensity, 0.9),
                repeat: Number.POSITIVE_INFINITY,
                ease: "easeInOut",
              }}
            />
          </g>
        ))}
      </svg>

      <div className="constellation-caption">
        <p className="eyebrow">Neural Constellation</p>
        <h2>The dream map</h2>
        <p>
          Observations drift in as pale sparks. Durable memories glow with stronger color. Each
          dream run leaves a warm disturbance where the night shift touched the graph.
        </p>
      </div>
    </div>
  );
}


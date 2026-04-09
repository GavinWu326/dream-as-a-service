import { motion } from "framer-motion";

const neurons = [
  { id: "n1", x: 16, y: 22, radius: 2.4, color: "#8fffcb", delay: 0.2 },
  { id: "n2", x: 31, y: 28, radius: 1.7, color: "#79dcff", delay: 0.6 },
  { id: "n3", x: 44, y: 19, radius: 2.1, color: "#ffd27a", delay: 1.0 },
  { id: "n4", x: 57, y: 31, radius: 2.8, color: "#f5a8ff", delay: 0.4 },
  { id: "n5", x: 69, y: 18, radius: 1.9, color: "#79dcff", delay: 1.2 },
  { id: "n6", x: 80, y: 30, radius: 2.3, color: "#8fffcb", delay: 0.8 },
  { id: "n7", x: 23, y: 56, radius: 2.9, color: "#ffd27a", delay: 1.5 },
  { id: "n8", x: 41, y: 48, radius: 1.8, color: "#79dcff", delay: 0.3 },
  { id: "n9", x: 59, y: 60, radius: 2.5, color: "#f5a8ff", delay: 1.1 },
  { id: "n10", x: 75, y: 55, radius: 1.9, color: "#8fffcb", delay: 0.9 },
  { id: "n11", x: 89, y: 68, radius: 2.2, color: "#ffd27a", delay: 1.8 },
  { id: "n12", x: 47, y: 79, radius: 3.1, color: "#79dcff", delay: 0.7 },
];

const links = [
  ["n1", "n2"],
  ["n2", "n3"],
  ["n2", "n7"],
  ["n3", "n4"],
  ["n4", "n5"],
  ["n4", "n8"],
  ["n5", "n6"],
  ["n7", "n8"],
  ["n8", "n9"],
  ["n8", "n12"],
  ["n9", "n10"],
  ["n10", "n11"],
  ["n9", "n12"],
  ["n6", "n10"],
];

const stars = [
  { id: "s1", x: 9, y: 14, size: 0.22, delay: 0.2 },
  { id: "s2", x: 27, y: 9, size: 0.18, delay: 1.2 },
  { id: "s3", x: 63, y: 10, size: 0.24, delay: 0.8 },
  { id: "s4", x: 85, y: 14, size: 0.18, delay: 1.8 },
  { id: "s5", x: 92, y: 24, size: 0.28, delay: 0.4 },
  { id: "s6", x: 11, y: 42, size: 0.2, delay: 1.4 },
  { id: "s7", x: 36, y: 37, size: 0.18, delay: 0.7 },
  { id: "s8", x: 53, y: 44, size: 0.22, delay: 1.7 },
  { id: "s9", x: 94, y: 53, size: 0.18, delay: 1.1 },
  { id: "s10", x: 7, y: 72, size: 0.25, delay: 0.9 },
  { id: "s11", x: 21, y: 82, size: 0.16, delay: 1.6 },
  { id: "s12", x: 64, y: 86, size: 0.22, delay: 0.5 },
  { id: "s13", x: 84, y: 83, size: 0.19, delay: 1.3 },
  { id: "s14", x: 43, y: 67, size: 0.15, delay: 0.6 },
];

const nodeById = new Map(neurons.map((node) => [node.id, node]));

export function HeroDreamscape() {
  return (
    <motion.div
      className="hero-dreamscape"
      initial={{ opacity: 0, y: 28, scale: 0.985 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 1.1, ease: "easeOut" }}
    >
      <div className="dream-haze haze-a" />
      <div className="dream-haze haze-b" />
      <div className="dream-haze haze-c" />

      <motion.span
        className="meteor meteor-a"
        animate={{ x: [0, 80], y: [0, 46], opacity: [0, 1, 0] }}
        transition={{ duration: 4.8, repeat: Number.POSITIVE_INFINITY, repeatDelay: 2.6, ease: "easeOut" }}
      />
      <motion.span
        className="meteor meteor-b"
        animate={{ x: [0, 65], y: [0, 38], opacity: [0, 0.9, 0] }}
        transition={{ duration: 4.2, repeat: Number.POSITIVE_INFINITY, repeatDelay: 3.4, ease: "easeOut", delay: 1.8 }}
      />

      <svg viewBox="0 0 100 100" className="dreamscape-svg" preserveAspectRatio="none">
        <defs>
          <radialGradient id="heroNodeGlow" cx="50%" cy="50%" r="60%">
            <stop offset="0%" stopColor="rgba(255,255,255,0.98)" />
            <stop offset="100%" stopColor="rgba(255,255,255,0)" />
          </radialGradient>
          <linearGradient id="heroLinkGlow" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="rgba(121,220,255,0.08)" />
            <stop offset="50%" stopColor="rgba(255,210,122,0.65)" />
            <stop offset="100%" stopColor="rgba(143,255,203,0.08)" />
          </linearGradient>
        </defs>

        {stars.map((star) => (
          <motion.circle
            key={star.id}
            cx={star.x}
            cy={star.y}
            r={star.size}
            fill="#ffffff"
            initial={{ opacity: 0.15 }}
            animate={{ opacity: [0.12, 0.78, 0.16], scale: [0.9, 1.25, 1] }}
            transition={{
              duration: 2.8,
              repeat: Number.POSITIVE_INFINITY,
              repeatDelay: 0.3,
              ease: "easeInOut",
              delay: star.delay,
            }}
          />
        ))}

        {links.map(([sourceId, targetId], index) => {
          const source = nodeById.get(sourceId);
          const target = nodeById.get(targetId);

          if (!source || !target) {
            return null;
          }

          return (
            <motion.line
              key={`${sourceId}-${targetId}`}
              x1={source.x}
              y1={source.y}
              x2={target.x}
              y2={target.y}
              stroke="url(#heroLinkGlow)"
              strokeWidth="0.32"
              strokeLinecap="round"
              initial={{ pathLength: 0, opacity: 0 }}
              animate={{ pathLength: 1, opacity: [0.16, 0.55, 0.18] }}
              transition={{
                duration: 3,
                repeat: Number.POSITIVE_INFINITY,
                repeatType: "mirror",
                ease: "easeInOut",
                delay: index * 0.12,
              }}
            />
          );
        })}

        {neurons.map((node) => (
          <g key={node.id}>
            <circle cx={node.x} cy={node.y} r={node.radius * 3.8} fill="url(#heroNodeGlow)" opacity="0.2" />
            <motion.circle
              cx={node.x}
              cy={node.y}
              r={node.radius}
              fill={node.color}
              initial={{ opacity: 0.5, scale: 0.95 }}
              animate={{ opacity: [0.45, 1, 0.62], scale: [1, 1.14, 1] }}
              transition={{
                duration: 3.4,
                repeat: Number.POSITIVE_INFINITY,
                ease: "easeInOut",
                delay: node.delay,
              }}
            />
          </g>
        ))}
      </svg>

      <div className="dreamscape-hud">
        <div className="dreamscape-labels">
          <span>Observation</span>
          <span>Dream</span>
          <span>Memory</span>
          <span>Recall</span>
        </div>
        <div className="dreamscape-note">
          <p className="eyebrow">Night Sky Interface</p>
          <h2>Signals crossing a sleeping mind</h2>
          <p>
            Synapses brighten where repeated facts cohere. Meteors mark fresh input cutting
            through the dark before the dream engine decides what deserves to stay.
          </p>
        </div>
      </div>
    </motion.div>
  );
}

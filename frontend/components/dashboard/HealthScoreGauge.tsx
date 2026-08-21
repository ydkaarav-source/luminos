"use client";

const SIZE = 120;
const STROKE = 10;
const RADIUS = (SIZE - STROKE) / 2;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

function colorForScore(score: number): string {
  if (score >= 75) return "#4ADE80"; // accent-bright
  if (score >= 50) return "#22C55E"; // accent-glow
  return "#F59E0B"; // brighter amber than the light-mode "warning" token - #B45309 is too dark to read against the night background
}

export function HealthScoreGauge({ score }: { score: number }) {
  const offset = CIRCUMFERENCE - (score / 100) * CIRCUMFERENCE;
  const color = colorForScore(score);

  return (
    <div className="relative" style={{ width: SIZE, height: SIZE }}>
      <svg width={SIZE} height={SIZE} className="-rotate-90">
        <circle
          cx={SIZE / 2}
          cy={SIZE / 2}
          r={RADIUS}
          stroke="#1E2E22"
          strokeWidth={STROKE}
          fill="none"
        />
        <circle
          cx={SIZE / 2}
          cy={SIZE / 2}
          r={RADIUS}
          stroke={color}
          strokeWidth={STROKE}
          strokeLinecap="round"
          fill="none"
          strokeDasharray={CIRCUMFERENCE}
          strokeDashoffset={offset}
          style={{ transition: "stroke-dashoffset 0.6s ease" }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-display text-2xl font-medium text-night-text">{score}</span>
        <span className="text-[10px] text-night-text-muted uppercase tracking-wide">/ 100</span>
      </div>
    </div>
  );
}

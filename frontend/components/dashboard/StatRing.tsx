"use client";

import { useEffect, useState } from "react";

interface Props {
  value: number;   // 0–100
  size?: number;
  strokeWidth?: number;
  label: string;
  sublabel?: string;
  color?: string;
}

export default function StatRing({
  value,
  size = 88,
  strokeWidth = 7,
  label,
  sublabel,
  color = "rgba(255,255,255,0.85)",
}: Props) {
  const [animated, setAnimated] = useState(false);
  const r = (size - strokeWidth) / 2;
  const circ = 2 * Math.PI * r;
  const offset = animated ? circ * (1 - value / 100) : circ;

  useEffect(() => {
    const t = setTimeout(() => setAnimated(true), 80);
    return () => clearTimeout(t);
  }, []);

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={r}
            fill="none"
            stroke="rgba(255,255,255,0.06)"
            strokeWidth={strokeWidth}
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={r}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circ}
            strokeDashoffset={offset}
            style={{ transition: "stroke-dashoffset 1s cubic-bezier(0.4,0,0.2,1)" }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-sm font-extrabold leading-none tabular-nums">{value}%</span>
        </div>
      </div>
      <div className="text-center">
        <p className="text-xs font-bold text-foreground">{label}</p>
        {sublabel && <p className="text-[10px] text-muted">{sublabel}</p>}
      </div>
    </div>
  );
}

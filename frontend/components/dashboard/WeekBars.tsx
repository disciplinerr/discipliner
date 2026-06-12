"use client";

import { useEffect, useState } from "react";

interface DayBar {
  date: string;
  pct: number;
  done: number;
  total: number;
}

interface Props {
  days: DayBar[];
}

const DAY_LABELS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const DAY_LABELS_PT = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"];

export default function WeekBars({ days }: Props) {
  const [animated, setAnimated] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setAnimated(true), 60);
    return () => clearTimeout(t);
  }, []);

  const today = new Date().toISOString().slice(0, 10);

  return (
    <div className="flex items-end gap-1.5 h-24 w-full">
      {days.map((d) => {
        const isToday = d.date === today;
        const height = animated ? `${Math.max(d.pct, 4)}%` : "4%";
        const dayIdx = new Date(d.date + "T12:00:00").getDay();
        const label = DAY_LABELS[dayIdx];

        return (
          <div key={d.date} className="flex flex-1 flex-col items-center gap-1.5">
            <div className="relative w-full flex-1 flex items-end">
              <div
                className="w-full rounded-t-md transition-all duration-700 ease-out"
                style={{
                  height,
                  background:
                    d.pct === 100
                      ? "rgba(255,255,255,0.9)"
                      : d.pct > 0
                        ? "rgba(255,255,255,0.35)"
                        : "rgba(255,255,255,0.06)",
                  transitionDelay: animated ? "0ms" : "0ms",
                }}
              />
              {isToday && (
                <span className="absolute -top-1 left-1/2 -translate-x-1/2 h-1 w-1 rounded-full bg-white/80" />
              )}
            </div>
            <span
              className={`text-[10px] font-bold uppercase tracking-wider select-none ${isToday ? "text-foreground" : "text-muted"}`}
            >
              {label}
            </span>
          </div>
        );
      })}
    </div>
  );
}

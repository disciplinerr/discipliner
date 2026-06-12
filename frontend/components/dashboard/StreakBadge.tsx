"use client";

import { useEffect, useState } from "react";

interface Props {
  streak: number;
}

export default function StreakBadge({ streak }: Props) {
  const [show, setShow] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setShow(true), 120);
    return () => clearTimeout(t);
  }, []);

  return (
    <div
      className={`flex flex-col items-center justify-center gap-1 transition-all duration-500 ${show ? "opacity-100 translate-y-0" : "opacity-0 translate-y-2"}`}
    >
      <span
        className="text-4xl font-extrabold tabular-nums leading-none"
        style={{ letterSpacing: "-0.03em" }}
      >
        {streak}
      </span>
      <span className="text-[10px] font-bold uppercase tracking-[0.18em] text-muted">
        day streak
      </span>
    </div>
  );
}

"use client";

import { useEffect, useRef, useState } from "react";
import { TrendPoint } from "@/types";
import { useI18n } from "@/lib/i18n";
import { formatMoney } from "@/lib/finance";

export default function TrendChart({ points }: { points: TrendPoint[] }) {
  const { t, locale } = useI18n();
  const [mounted, setMounted] = useState(false);
  const [active, setActive] = useState<number | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Trigger the grow-in transition one frame after mount so the bars animate
  // from zero height instead of snapping to their final size.
  useEffect(() => {
    const id = requestAnimationFrame(() => setMounted(true));
    return () => cancelAnimationFrame(id);
  }, []);

  if (points.length === 0) {
    return <p className="text-sm text-muted">{t("finance.no_trend")}</p>;
  }

  // Shared scale across both series so bar heights are comparable month to month.
  const max = Math.max(1, ...points.map((p) => Math.max(p.income, p.expense)));

  const monthLabel = (p: TrendPoint) =>
    new Date(p.year, p.month - 1, 1).toLocaleDateString(
      locale === "pt-BR" ? "pt-BR" : "en-US",
      { month: "short" },
    );

  const sel = active != null ? points[active] : null;

  return (
    <div ref={containerRef} className="relative select-none">
      {/* Tooltip */}
      {sel && (
        <div
          className="pointer-events-none absolute z-10 -translate-x-1/2 rounded-xl border border-line bg-elevated/95 px-3 py-2 shadow-soft backdrop-blur-sm transition-all duration-150"
          style={{
            left: `${((active! + 0.5) / points.length) * 100}%`,
            top: 0,
          }}
        >
          <p className="mb-1 text-[11px] font-bold capitalize text-foreground">
            {monthLabel(sel)} {sel.year}
          </p>
          <div className="space-y-0.5 text-[11px] whitespace-nowrap">
            <p className="flex items-center justify-between gap-3">
              <span className="flex items-center gap-1.5 text-muted">
                <span className="h-2 w-2 rounded-full bg-emerald-400" />
                {t("finance.income")}
              </span>
              <span className="font-bold text-emerald-400">
                {formatMoney(sel.income, locale)}
              </span>
            </p>
            <p className="flex items-center justify-between gap-3">
              <span className="flex items-center gap-1.5 text-muted">
                <span className="h-2 w-2 rounded-full bg-rose-400" />
                {t("finance.expense")}
              </span>
              <span className="font-bold text-rose-400">
                {formatMoney(sel.expense, locale)}
              </span>
            </p>
            <p className="flex items-center justify-between gap-3 border-t border-line pt-0.5">
              <span className="text-muted">{t("finance.balance")}</span>
              <span
                className={`font-bold ${
                  sel.balance >= 0 ? "text-foreground" : "text-rose-400"
                }`}
              >
                {formatMoney(sel.balance, locale)}
              </span>
            </p>
          </div>
        </div>
      )}

      {/* Bars */}
      <div className="flex items-end justify-between gap-1 pt-16 sm:gap-3">
        {points.map((p, i) => {
          const isActive = active === i;
          const dim = active != null && !isActive;
          return (
            <div
              key={`${p.year}-${p.month}`}
              className="group flex flex-1 cursor-pointer flex-col items-center gap-1"
              onMouseEnter={() => setActive(i)}
              onMouseLeave={() => setActive(null)}
              onClick={() => setActive((cur) => (cur === i ? null : i))}
            >
              <div
                className={`relative flex h-28 w-full items-end justify-center gap-1 rounded-md transition-colors duration-200 ${
                  isActive ? "bg-foreground/5" : ""
                }`}
              >
                <div
                  className={`w-1/2 max-w-[16px] rounded-t bg-emerald-400 transition-all duration-700 ease-out ${
                    dim ? "opacity-40" : "opacity-90"
                  }`}
                  style={{
                    height: mounted ? `${(p.income / max) * 100}%` : "0%",
                    transitionDelay: `${i * 60}ms`,
                  }}
                />
                <div
                  className={`w-1/2 max-w-[16px] rounded-t bg-rose-400 transition-all duration-700 ease-out ${
                    dim ? "opacity-40" : "opacity-90"
                  }`}
                  style={{
                    height: mounted ? `${(p.expense / max) * 100}%` : "0%",
                    transitionDelay: `${i * 60 + 90}ms`,
                  }}
                />
              </div>
              <span
                className={`text-[10px] font-semibold capitalize transition-colors duration-200 ${
                  isActive ? "text-foreground" : "text-muted"
                }`}
              >
                {monthLabel(p)}
              </span>
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="mt-3 flex items-center justify-center gap-4 text-[11px] text-muted">
        <span className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-emerald-400" /> {t("finance.income")}
        </span>
        <span className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-rose-400" /> {t("finance.expense")}
        </span>
      </div>
    </div>
  );
}

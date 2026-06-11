"use client";

import { useEffect, useState } from "react";
import { getMonthRoutine } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import { RoutineMonth } from "@/types";

const WEEKDAYS_PT = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"];
const WEEKDAYS_EN = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

function dayColor(done: number, total: number, skipped: number, isFuture: boolean): string {
  if (isFuture || total === 0) return "bg-transparent";
  if (done === 0 && skipped === 0) return "bg-red-500/20 text-red-400";
  const ratio = done / total;
  if (ratio >= 1) return "bg-foreground text-background";
  if (ratio >= 0.6) return "bg-neutral-500/50 text-foreground";
  if (ratio >= 0.3) return "bg-amber-500/30 text-amber-300";
  return "bg-red-500/20 text-red-400";
}

export default function RoutineCalendar() {
  const { t, locale } = useI18n();
  const today = new Date();
  const [year, setYear] = useState(today.getFullYear());
  const [month, setMonth] = useState(today.getMonth() + 1);
  const [data, setData] = useState<RoutineMonth | null>(null);

  useEffect(() => {
    setData(null);
    getMonthRoutine(year, month).then(setData).catch(() => {});
  }, [year, month]);

  function prev() {
    if (month === 1) { setYear(y => y - 1); setMonth(12); }
    else setMonth(m => m - 1);
  }
  function next() {
    const now = new Date();
    if (year > now.getFullYear() || (year === now.getFullYear() && month >= now.getMonth() + 1)) return;
    if (month === 12) { setYear(y => y + 1); setMonth(1); }
    else setMonth(m => m + 1);
  }

  const isPt = locale.startsWith("pt");
  const weekdays = isPt ? WEEKDAYS_PT : WEEKDAYS_EN;
  const monthName = new Date(year, month - 1, 1).toLocaleString(locale, { month: "long", year: "numeric" });

  // Build calendar grid (Mon-based, ISO week)
  const firstDate = new Date(year, month - 1, 1);
  const startOffset = (firstDate.getDay() + 6) % 7; // 0=Mon
  const totalDays = data?.days.length ?? new Date(year, month, 0).getDate();

  const cells: (number | null)[] = [
    ...Array(startOffset).fill(null),
    ...Array.from({ length: totalDays }, (_, i) => i + 1),
  ];
  // Pad to complete last row
  while (cells.length % 7 !== 0) cells.push(null);

  const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`;

  function getSummary(day: number) {
    const dateStr = `${year}-${String(month).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
    return data?.days.find(d => d.date === dateStr);
  }

  const isAtMax = year > today.getFullYear() || (year === today.getFullYear() && month >= today.getMonth() + 1);

  return (
    <div className="space-y-3">
      {/* Navigation */}
      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={prev}
          className="rounded-lg px-3 py-1 text-xs font-bold text-muted transition-colors hover:text-foreground"
        >
          ←
        </button>
        <span className="text-sm font-bold capitalize text-secondary">{monthName}</span>
        <button
          type="button"
          onClick={next}
          disabled={isAtMax}
          className="rounded-lg px-3 py-1 text-xs font-bold text-muted transition-colors hover:text-foreground disabled:opacity-30"
        >
          →
        </button>
      </div>

      {/* Day headers */}
      <div className="grid grid-cols-7 gap-1">
        {weekdays.map(d => (
          <div key={d} className="text-center text-[10px] font-bold uppercase tracking-wider text-muted py-1">
            {d}
          </div>
        ))}

        {/* Day cells */}
        {cells.map((day, idx) => {
          if (day === null) return <div key={`empty-${idx}`} />;
          const dateStr = `${year}-${String(month).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
          const summary = getSummary(day);
          const isFuture = dateStr > todayStr;
          const isToday = dateStr === todayStr;
          const colorClass = summary
            ? dayColor(summary.done, summary.total, summary.skipped, isFuture)
            : isFuture ? "bg-transparent text-muted/30" : "bg-transparent text-muted";

          return (
            <div
              key={day}
              title={
                summary && !isFuture
                  ? `${summary.done}/${summary.total} ${isPt ? "feitos" : "done"}`
                  : undefined
              }
              className={`relative flex h-8 w-full items-center justify-center rounded-lg text-xs font-semibold transition-colors ${colorClass} ${
                isToday ? "ring-1 ring-foreground/50" : ""
              }`}
            >
              {day}
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-x-4 gap-y-1 pt-1">
        {[
          { cls: "bg-foreground", label: t("routine.calendar_all_done") },
          { cls: "bg-neutral-500/50", label: t("routine.calendar_partial") },
          { cls: "bg-red-500/20", label: t("routine.calendar_missed") },
        ].map(({ cls, label }) => (
          <div key={label} className="flex items-center gap-1.5">
            <span className={`h-2.5 w-2.5 rounded-sm ${cls}`} />
            <span className="text-[11px] text-muted">{label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

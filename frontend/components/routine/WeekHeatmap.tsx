"use client";

import { routineLabel, useI18n } from "@/lib/i18n";
import { RoutineWeek } from "@/types";

const CELL: Record<string, string> = {
  DONE: "bg-foreground",
  LATE: "bg-neutral-500",
  SKIPPED: "bg-neutral-700",
};

export default function WeekHeatmap({ week }: { week: RoutineWeek }) {
  const { t, locale } = useI18n();
  if (week.days.length === 0) return null;
  const itemKeys = week.days[0].items.map((i) => ({
    key: i.item_key,
    label: i.label,
  }));

  return (
    <div>
      <div className="overflow-x-auto">
        <table className="w-full border-separate border-spacing-1 text-xs">
          <thead>
            <tr>
              <th className="pr-3 text-left font-semibold text-muted" />
              {week.days.map((day) => (
                <th key={day.date} className="pb-1 font-semibold text-muted">
                  {new Date(day.date + "T12:00:00").toLocaleDateString(locale, {
                    weekday: "short",
                  })}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {itemKeys.map(({ key, label }) => {
              const translated = routineLabel(t, key, label);
              return (
                <tr key={key}>
                  <td
                    className="max-w-[180px] truncate pr-3 text-secondary"
                    title={translated}
                  >
                    {translated}
                  </td>
                  {week.days.map((day) => {
                    const item = day.items.find((i) => i.item_key === key);
                    const status = item?.status ?? null;
                    return (
                      <td key={day.date}>
                        <div
                          title={`${day.date}: ${status ?? t("routine.not_logged")}`}
                          className={`h-6 w-full min-w-6 rounded-md transition-transform hover:scale-110 ${
                            status ? CELL[status] : "bg-elevated"
                          }`}
                        />
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="mt-4 flex flex-wrap gap-4 text-xs text-muted">
        <span className="flex items-center gap-1.5">
          <span className="h-3 w-3 rounded bg-foreground" /> {t("routine.legend_done")}
        </span>
        <span className="flex items-center gap-1.5">
          <span className="h-3 w-3 rounded bg-neutral-500" /> {t("routine.legend_late")}
        </span>
        <span className="flex items-center gap-1.5">
          <span className="h-3 w-3 rounded bg-neutral-700" />{" "}
          {t("routine.legend_skipped")}
        </span>
        <span className="flex items-center gap-1.5">
          <span className="h-3 w-3 rounded bg-elevated" /> {t("routine.legend_empty")}
        </span>
      </div>
    </div>
  );
}

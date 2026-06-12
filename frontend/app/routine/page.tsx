"use client";

import { useCallback, useEffect, useState } from "react";
import PomodoroTimer from "@/components/routine/PomodoroTimer";
import RoutineCalendar from "@/components/routine/RoutineCalendar";
import RoutineChecklist from "@/components/routine/RoutineChecklist";
import RoutineItemManagerModal from "@/components/routine/RoutineItemManagerModal";
import RoutineReminders from "@/components/routine/RoutineReminders";
import WeekHeatmap from "@/components/routine/WeekHeatmap";
import Card from "@/components/ui/Card";
import ProgressBar from "@/components/ui/ProgressBar";
import RequireAuth from "@/components/ui/RequireAuth";
import { getTodayRoutine, getWeekRoutine } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import { RoutineDay, RoutineWeek } from "@/types";

export default function RoutinePage() {
  const { t } = useI18n();
  const [today, setToday] = useState<RoutineDay | null>(null);
  const [week, setWeek] = useState<RoutineWeek | null>(null);
  const [showManager, setShowManager] = useState(false);

  const load = useCallback(() => {
    getTodayRoutine().then(setToday).catch(() => {});
    getWeekRoutine().then(setWeek).catch(() => {});
  }, []);

  useEffect(load, [load]);

  const done = today ? today.items.filter((i) => i.status !== null).length : 0;
  const total = today?.items.length ?? 0;
  const pending = today ? today.items.filter((i) => i.status === null).length : 0;

  return (
    <RequireAuth>
      <div className="space-y-6">
        <div className="animate-fade-up">
          <h1 className="text-3xl font-extrabold tracking-tight">
            {t("routine.title")}
          </h1>
          <p className="mt-1 text-secondary">{t("routine.subtitle")}</p>
        </div>

        {/* Today checklist */}
        <Card
          title={t("routine.today")}
          action={
            <div className="flex items-center gap-3">
              {today && (
                <span className="text-sm font-bold text-secondary">
                  {done}/{total}
                </span>
              )}
              <button
                type="button"
                onClick={() => setShowManager((v) => !v)}
                className="rounded-lg border border-line px-2.5 py-1 text-[11px] font-bold text-muted transition-colors hover:border-secondary hover:text-foreground"
              >
                {t("routine.manage_items")}
              </button>
            </div>
          }
        >
          {today ? (
            <>
              <ProgressBar value={done} total={total} className="mb-4" />
              <RoutineChecklist items={today.items} onChange={load} />
            </>
          ) : (
            <p className="text-sm text-muted">{t("common.loading")}</p>
          )}

        </Card>

        <Card title={t("routine.pomodoro")}>
          <PomodoroTimer />
        </Card>

        {/* Reminders */}
        <Card title={t("routine.reminders")}>
          <RoutineReminders pendingCount={pending} />
        </Card>

        {/* Weekly heatmap */}
        <Card title={t("routine.last7")}>
          {week ? (
            <WeekHeatmap week={week} />
          ) : (
            <p className="text-sm text-muted">{t("common.loading")}</p>
          )}
        </Card>

        {/* Monthly calendar */}
        <Card title={t("routine.calendar")}>
          <RoutineCalendar />
        </Card>
      </div>

      {showManager && (
        <RoutineItemManagerModal
          onClose={() => setShowManager(false)}
          onChanged={load}
        />
      )}
    </RequireAuth>
  );
}

"use client";

import { useCallback, useEffect, useState } from "react";
import PomodoroTimer from "@/components/routine/PomodoroTimer";
import RoutineChecklist from "@/components/routine/RoutineChecklist";
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

  const load = useCallback(() => {
    getTodayRoutine().then(setToday).catch(() => {});
    getWeekRoutine().then(setWeek).catch(() => {});
  }, []);

  useEffect(load, [load]);

  const done = today ? today.items.filter((i) => i.status !== null).length : 0;
  const total = today?.items.length ?? 0;

  return (
    <RequireAuth>
      <div className="space-y-6">
        <div className="animate-fade-up">
          <h1 className="text-3xl font-extrabold tracking-tight">
            {t("routine.title")}
          </h1>
          <p className="mt-1 text-secondary">{t("routine.subtitle")}</p>
        </div>

        <Card
          title={t("routine.today")}
          action={
            today && (
              <span className="text-sm font-bold text-secondary">
                {done}/{total}
              </span>
            )
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

        <Card title={t("routine.last7")}>
          {week ? (
            <WeekHeatmap week={week} />
          ) : (
            <p className="text-sm text-muted">{t("common.loading")}</p>
          )}
        </Card>
      </div>
    </RequireAuth>
  );
}

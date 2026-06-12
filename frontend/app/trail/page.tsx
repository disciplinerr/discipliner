"use client";

import { useCallback, useEffect, useState } from "react";
import PhaseCard from "@/components/trail/PhaseCard";
import ProgressBar from "@/components/ui/ProgressBar";
import RequireAuth from "@/components/ui/RequireAuth";
import { getTrailProgress } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import { TrailProgress } from "@/types";

export default function TrailPage() {
  const { t } = useI18n();
  const [progress, setProgress] = useState<TrailProgress | null>(null);
  const [expanded, setExpanded] = useState<number | null>(null);

  const load = useCallback(() => {
    getTrailProgress().then((data) => {
      setProgress(data);
      // Auto-expand the current phase on first load.
      setExpanded((prev) => {
        if (prev !== null) return prev;
        return data.phases.find((p) => p.is_current)?.phase.id ?? null;
      });
    }).catch(() => {});
  }, []);

  useEffect(load, [load]);

  const completed =
    progress?.phases.filter((p) => p.completed_at !== null).length ?? 0;
  const total = progress?.phases.length ?? 6;

  return (
    <RequireAuth>
      <div className="space-y-8">
        <div className="animate-fade-up">
          <h1 className="text-3xl font-extrabold tracking-tight">{t("trail.title")}</h1>
          <p className="mt-1 text-secondary">{t("trail.subtitle")}</p>
          <div className="mt-4 flex items-center gap-3">
            <ProgressBar value={completed} total={total} className="max-w-xs" />
            <span className="text-sm font-bold text-secondary">
              {completed}/{total} {t("trail.phases")}
            </span>
          </div>
        </div>

        {progress ? (
          <ul className="animate-fade-up">
            {progress.phases.map((p, idx) => (
              <PhaseCard
                key={p.phase.id}
                progress={p}
                isLast={idx === progress.phases.length - 1}
                expanded={expanded === p.phase.id}
                onToggle={() =>
                  setExpanded(expanded === p.phase.id ? null : p.phase.id)
                }
                onCompleted={() => {
                  setExpanded(null);
                  load();
                }}
              />
            ))}
          </ul>
        ) : (
          <p className="text-sm text-muted">{t("common.loading")}</p>
        )}
      </div>
    </RequireAuth>
  );
}

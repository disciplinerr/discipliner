"use client";

import { FormEvent, useState } from "react";
import Button from "@/components/ui/Button";
import { ApiError, completePhase } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import { PhaseProgress } from "@/types";
import { Check } from "lucide-react";

export default function PhaseCard({
  progress,
  isLast,
  expanded,
  onToggle,
  onCompleted,
}: {
  progress: PhaseProgress;
  isLast: boolean;
  expanded: boolean;
  onToggle: () => void;
  onCompleted: () => void;
}) {
  const { t } = useI18n();
  const { phase } = progress;
  const [summary, setSummary] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const done = progress.completed_at !== null;
  const current = progress.is_current;
  const locked = !done && !current;

  async function handleComplete(e: FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await completePhase(phase.id, summary);
      onCompleted();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("trail.complete_failed"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <li className="relative pl-12">
      {/* Connector line */}
      {!isLast && (
        <span
          aria-hidden
          className={`absolute left-[15px] top-10 h-[calc(100%-24px)] w-0.5 ${
            done ? "bg-foreground" : "bg-line"
          }`}
        />
      )}

      {/* Step marker */}
      <span
        aria-hidden
        className={`absolute left-0 top-1.5 flex h-8 w-8 items-center justify-center rounded-full text-sm font-extrabold transition-colors ${
          done
            ? "bg-foreground text-background"
            : current
              ? "border-2 border-foreground bg-background text-foreground"
              : "border border-line bg-surface text-muted"
        }`}
      >
        {done ? <Check size={16} /> : phase.number}
      </span>

      <div
        className={`mb-6 overflow-hidden rounded-2xl border transition-colors ${
          current ? "border-secondary bg-surface" : "border-line bg-surface"
        } ${locked ? "opacity-60" : ""}`}
      >
        <button
          type="button"
          onClick={onToggle}
          className="flex w-full items-center justify-between gap-4 p-5 text-left"
        >
          <div>
            <h3 className="font-extrabold tracking-tight">{phase.name}</h3>
            <p className="mt-0.5 text-xs font-semibold text-muted">
              {phase.weeks}
              {done && ` · ${t("trail.completed")}`}
              {current && ` · ${t("trail.current")}`}
              {locked && ` · ${t("trail.locked")}`}
            </p>
          </div>
          <span
            className={`text-muted transition-transform duration-300 ${
              expanded ? "rotate-180" : ""
            }`}
          >
            ▾
          </span>
        </button>

        <div
          className={`grid transition-all duration-300 ease-out ${
            expanded ? "grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0"
          }`}
        >
          <div className="overflow-hidden">
            <div className="border-t border-line p-5">
              <div className="grid gap-6 text-sm sm:grid-cols-2">
                <div>
                  <h4 className="mb-2 text-xs font-bold uppercase tracking-[0.18em] text-muted">
                    {t("trail.topics")}
                  </h4>
                  <ul className="space-y-1.5">
                    {phase.topics.map((t) => (
                      <li key={t} className="flex items-center gap-2 text-secondary">
                        <span className="h-1 w-1 shrink-0 rounded-full bg-muted" />
                        {t}
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h4 className="mb-2 text-xs font-bold uppercase tracking-[0.18em] text-muted">
                    {t("trail.exercises")}
                  </h4>
                  <ul className="space-y-1.5">
                    {phase.exercises.map((e) => (
                      <li key={e} className="flex items-center gap-2 text-secondary">
                        <span className="h-1 w-1 shrink-0 rounded-full bg-muted" />
                        {e}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {done && progress.summary && (
                <div className="mt-5 rounded-xl bg-elevated p-4 text-sm text-secondary">
                  <p className="mb-1 text-xs font-bold uppercase tracking-[0.18em] text-muted">
                    {t("trail.your_summary")}
                  </p>
                  {progress.summary}
                </div>
              )}

              {current && !done && (
                <form onSubmit={handleComplete} className="mt-5 space-y-3">
                  <label className="block text-xs font-bold uppercase tracking-[0.18em] text-muted">
                    {t("trail.feynman_label")}
                  </label>
<p className="text-xs text-secondary">{t("trail.feynman_help")}</p>
                  <textarea
                    value={summary}
                    onChange={(e) => setSummary(e.target.value)}
                    rows={5}
                    minLength={100}
                    required
                    placeholder={t("trail.feynman_placeholder")}
                    className="w-full rounded-xl border border-line bg-elevated p-4 text-sm text-foreground placeholder:text-muted transition-colors focus:border-secondary"
                  />
                  <div className="flex items-center justify-between">
                    <span
                      className={`text-xs font-semibold ${
                        summary.length >= 100 ? "text-secondary" : "text-muted"
                      }`}
                    >
                      {summary.length}/100
                    </span>
                    <Button type="submit" disabled={busy || summary.length < 100}>
                      {busy ? "..." : t("trail.complete")}
                    </Button>
                  </div>
                  {error && <p className="text-sm text-red-400">{error}</p>}
                </form>
              )}
            </div>
          </div>
        </div>
      </div>
    </li>
  );
}

"use client";

import { useCallback, useEffect, useState } from "react";
import Card from "@/components/ui/Card";
import RequireAuth from "@/components/ui/RequireAuth";
import { getDueReviews, getReviewStats, gradeReview } from "@/lib/api";
import { TKey, useI18n } from "@/lib/i18n";
import { ReviewCard, ReviewStats } from "@/types";

const GRADES: { value: 0 | 1 | 2 | 3; label: TKey; hint: TKey }[] = [
  { value: 0, label: "review.grade0", hint: "review.grade0_hint" },
  { value: 1, label: "review.grade1", hint: "review.grade1_hint" },
  { value: 2, label: "review.grade2", hint: "review.grade2_hint" },
  { value: 3, label: "review.grade3", hint: "review.grade3_hint" },
];

export default function ReviewPage() {
  const { t } = useI18n();
  const [queue, setQueue] = useState<ReviewCard[] | null>(null);
  const [stats, setStats] = useState<ReviewStats | null>(null);
  const [revealed, setRevealed] = useState(false);
  const [busy, setBusy] = useState(false);

  const load = useCallback(() => {
    getDueReviews().then(setQueue).catch(() => {});
    getReviewStats().then(setStats).catch(() => {});
  }, []);

  useEffect(load, [load]);

  const current = queue?.[0] ?? null;

  async function grade(value: 0 | 1 | 2 | 3) {
    if (!current || busy) return;
    setBusy(true);
    try {
      await gradeReview(current.id, value);
      setRevealed(false);
      setQueue((q) => (q ? q.slice(1) : q));
      getReviewStats().then(setStats).catch(() => {});
    } finally {
      setBusy(false);
    }
  }

  return (
    <RequireAuth>
      <div className="space-y-6">
        <div className="animate-fade-up">
          <h1 className="text-3xl font-extrabold tracking-tight">
            {t("review.title")}
          </h1>
          <p className="mt-1 text-secondary">{t("review.subtitle")}</p>
        </div>

        {stats && (
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {[
              { label: t("review.due_today"), value: stats.due },
              { label: t("review.reviewed_today"), value: stats.reviewed_today },
              { label: t("review.mature"), value: stats.mature },
              { label: t("review.total"), value: stats.total },
            ].map((s) => (
              <div
                key={s.label}
                className="animate-fade-up rounded-2xl border border-line bg-surface p-4 text-center"
              >
                <p className="text-2xl font-extrabold">{s.value}</p>
                <p className="text-xs font-semibold text-muted">{s.label}</p>
              </div>
            ))}
          </div>
        )}

        {queue === null ? (
          <p className="text-sm text-muted">{t("common.loading")}</p>
        ) : current ? (
          <Card>
            <div className="flex min-h-[280px] flex-col items-center justify-center gap-6 py-6 text-center">
              <span className="rounded-full border border-line px-3 py-1 text-xs font-bold text-muted">
                {queue.length}{" "}
                {queue.length === 1 ? t("review.card_left") : t("review.cards_left")}
              </span>

              <div>
                <p className="mb-2 text-xs font-bold uppercase tracking-[0.18em] text-muted">
                  {t("review.explain")}
                </p>
                <h2 className="text-2xl font-extrabold tracking-tight sm:text-3xl">
                  {current.topic}
                </h2>
              </div>

              {!revealed ? (
                <>
                  <p className="max-w-md text-sm text-secondary">
                    {t("review.instruction")}
                  </p>
                  <button
                    onClick={() => setRevealed(true)}
                    className="rounded-xl bg-foreground px-6 py-2.5 text-sm font-bold text-background transition-all hover:bg-neutral-300 active:scale-[0.98]"
                  >
                    {t("review.reveal")}
                  </button>
                </>
              ) : (
                <div className="grid w-full max-w-md grid-cols-2 gap-2 sm:grid-cols-4">
                  {GRADES.map((g) => (
                    <button
                      key={g.value}
                      onClick={() => grade(g.value)}
                      disabled={busy}
                      className={`rounded-xl border p-3 transition-all active:scale-[0.97] disabled:opacity-40 ${
                        g.value === 0
                          ? "border-line text-red-400 hover:border-red-400"
                          : g.value === 3
                            ? "border-foreground bg-foreground text-background hover:bg-neutral-300"
                            : "border-line text-secondary hover:border-muted hover:text-foreground"
                      }`}
                    >
                      <span className="block text-sm font-bold">{t(g.label)}</span>
                      <span className="block text-[10px] opacity-70">{t(g.hint)}</span>
                    </button>
                  ))}
                </div>
              )}

              <p className="text-xs text-muted">
                {t("review.interval")}: {current.interval_days}d ·{" "}
                {t("review.repetitions")}: {current.repetitions}
              </p>
            </div>
          </Card>
        ) : (
          <Card>
            <div className="flex min-h-[200px] flex-col items-center justify-center gap-3 text-center">
              <span className="flex h-12 w-12 items-center justify-center rounded-full bg-foreground text-xl text-background">
                ✓
              </span>
              <p className="font-extrabold">{t("review.done_title")}</p>
              <p className="max-w-sm text-sm text-secondary">{t("review.done_text")}</p>
            </div>
          </Card>
        )}
      </div>
    </RequireAuth>
  );
}

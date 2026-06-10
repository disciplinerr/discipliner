"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import Card from "@/components/ui/Card";
import ProgressBar from "@/components/ui/ProgressBar";
import RequireAuth from "@/components/ui/RequireAuth";
import {
  getChallengeHistory,
  getReviewStats,
  getTodayRoutine,
  getTrailProgress,
} from "@/lib/api";
import { routineLabel, useI18n } from "@/lib/i18n";
import {
  ChallengeHistoryItem,
  ReviewStats,
  RoutineDay,
  TrailProgress,
} from "@/types";

const RESULT_STYLE: Record<string, string> = {
  PASS: "bg-foreground text-background",
  FAIL: "border border-line text-red-400",
  PARTIAL: "border border-line text-secondary",
  PENDING: "border border-line text-muted",
};

export default function DashboardPage() {
  const { t, locale } = useI18n();
  const [routine, setRoutine] = useState<RoutineDay | null>(null);
  const [history, setHistory] = useState<ChallengeHistoryItem[] | null>(null);
  const [trail, setTrail] = useState<TrailProgress | null>(null);
  const [reviews, setReviews] = useState<ReviewStats | null>(null);

  useEffect(() => {
    getTodayRoutine().then(setRoutine).catch(() => {});
    getChallengeHistory().then(setHistory).catch(() => {});
    getTrailProgress().then(setTrail).catch(() => {});
    getReviewStats().then(setReviews).catch(() => {});
  }, []);

  const routineDone = routine
    ? routine.items.filter((i) => i.status !== null).length
    : 0;
  const routineTotal = routine?.items.length ?? 0;

  const today = new Date().toISOString().slice(0, 10);
  const todayItem = history?.find((h) => h.challenge.date === today);
  const challengeResult = todayItem?.submissions[0]?.result ?? null;

  const currentPhase = trail?.phases.find((p) => p.is_current);
  const completedPhases =
    trail?.phases.filter((p) => p.completed_at !== null).length ?? 0;
  const totalPhases = trail?.phases.length ?? 6;

  const hour = new Date().getHours();
  const greeting =
    hour < 12
      ? t("dashboard.greeting_morning")
      : hour < 18
        ? t("dashboard.greeting_afternoon")
        : t("dashboard.greeting_evening");

  return (
    <RequireAuth>
      <div className="space-y-6">
        <div className="animate-fade-up">
          <h1 className="text-3xl font-extrabold tracking-tight">{greeting}</h1>
          <p className="mt-1 text-secondary">
            {new Date().toLocaleDateString(locale, {
              weekday: "long",
              day: "numeric",
              month: "long",
            })}
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Link href="/routine" className="group">
            <Card className="h-full transition-colors group-hover:border-muted">
              <p className="text-xs font-bold uppercase tracking-[0.18em] text-muted">
                {t("dashboard.routine")}
              </p>
              <p className="mt-3 text-3xl font-extrabold">
                {routine ? (
                  <>
                    {routineDone}
                    <span className="text-lg font-semibold text-muted">
                      /{routineTotal}
                    </span>
                  </>
                ) : (
                  "—"
                )}
              </p>
              <p className="mb-3 mt-1 text-sm text-secondary">
                {t("dashboard.items_logged")}
              </p>
              <ProgressBar value={routineDone} total={routineTotal} />
            </Card>
          </Link>

          <Link href="/challenges" className="group">
            <Card className="h-full transition-colors group-hover:border-muted">
              <p className="text-xs font-bold uppercase tracking-[0.18em] text-muted">
                {t("dashboard.challenge")}
              </p>
              <div className="mt-3">
                {challengeResult ? (
                  <span
                    className={`inline-block rounded-full px-3 py-1 text-sm font-bold ${RESULT_STYLE[challengeResult]}`}
                  >
                    {challengeResult}
                  </span>
                ) : (
                  <span className="inline-block rounded-full border border-dashed border-line px-3 py-1 text-sm font-semibold text-muted">
                    {history === null
                      ? "—"
                      : todayItem
                        ? t("dashboard.not_attempted")
                        : t("dashboard.not_generated")}
                  </span>
                )}
              </div>
              <p className="mt-3 text-sm text-secondary">
                {todayItem ? todayItem.challenge.title : t("dashboard.open_today")}
              </p>
            </Card>
          </Link>

          <Link href="/review" className="group">
            <Card className="h-full transition-colors group-hover:border-muted">
              <p className="text-xs font-bold uppercase tracking-[0.18em] text-muted">
                {t("dashboard.review")}
              </p>
              <p className="mt-3 text-3xl font-extrabold">
                {reviews ? (
                  <>
                    {reviews.due}
                    <span className="text-lg font-semibold text-muted">
                      {" "}
                      {t("dashboard.cards")}
                    </span>
                  </>
                ) : (
                  "—"
                )}
              </p>
              <p className="mb-3 mt-1 text-sm text-secondary">
                {reviews && reviews.due === 0
                  ? t("dashboard.all_caught_up")
                  : t("dashboard.pending_cards")}
              </p>
              <ProgressBar
                value={reviews?.reviewed_today ?? 0}
                total={(reviews?.reviewed_today ?? 0) + (reviews?.due ?? 0)}
              />
            </Card>
          </Link>

          <Link href="/trail" className="group">
            <Card className="h-full transition-colors group-hover:border-muted">
              <p className="text-xs font-bold uppercase tracking-[0.18em] text-muted">
                {t("dashboard.trail")}
              </p>
              <p className="mt-3 text-3xl font-extrabold">
                {trail ? (
                  <>
                    {trail.current_phase}
                    <span className="text-lg font-semibold text-muted">
                      /{totalPhases}
                    </span>
                  </>
                ) : (
                  "—"
                )}
              </p>
              <p className="mb-3 mt-1 text-sm text-secondary">
                {currentPhase ? currentPhase.phase.name : t("dashboard.current_phase")}
              </p>
              <ProgressBar value={completedPhases} total={totalPhases} />
            </Card>
          </Link>
        </div>

        {routine && routineDone < routineTotal && (
          <Card title={t("dashboard.pending_today")}>
            <ul className="space-y-2">
              {routine.items
                .filter((i) => i.status === null)
                .map((i) => (
                  <li key={i.item_key} className="flex items-center gap-3 text-sm">
                    <span className="h-1.5 w-1.5 rounded-full bg-muted" />
                    <span className="text-secondary">
                      {routineLabel(t, i.item_key, i.label)}
                    </span>
                  </li>
                ))}
            </ul>
            <Link
              href="/routine"
              className="mt-4 inline-block text-sm font-bold text-foreground underline-offset-4 hover:underline"
            >
              {t("dashboard.go_routine")}
            </Link>
          </Card>
        )}
      </div>
    </RequireAuth>
  );
}

"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import StreakBadge from "@/components/dashboard/StreakBadge";
import StatRing from "@/components/dashboard/StatRing";
import WeekBars from "@/components/dashboard/WeekBars";
import TrendChart from "@/components/finance/TrendChart";
import Card from "@/components/ui/Card";
import ProgressBar from "@/components/ui/ProgressBar";
import RequireAuth from "@/components/ui/RequireAuth";
import {
  getChallengeHistory,
  getDashboardStats,
  getFinanceOverview,
  getReviewStats,
  getTodayRoutine,
  getTrailProgress,
  getTrend,
} from "@/lib/api";
import { formatMoney } from "@/lib/finance";
import { routineLabel, TKey, useI18n } from "@/lib/i18n";
import {
  ChallengeHistoryItem,
  DashboardStats,
  FinanceOverview,
  ReviewStats,
  RoutineDay,
  TrailProgress,
  TrendPoint,
} from "@/types";

const FINANCE_STATUS_STYLE: Record<string, string> = {
  healthy: "border-emerald-500/40 text-emerald-400",
  tight: "border-amber-500/40 text-amber-400",
  over: "border-rose-500/40 text-rose-400",
  unknown: "border-line text-muted",
};

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
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [finance, setFinance] = useState<FinanceOverview | null>(null);
  const [trend, setTrend] = useState<TrendPoint[]>([]);

  useEffect(() => {
    const now = new Date();
    getTodayRoutine().then(setRoutine).catch(() => {});
    getChallengeHistory().then(setHistory).catch(() => {});
    getTrailProgress().then(setTrail).catch(() => {});
    getReviewStats().then(setReviews).catch(() => {});
    getDashboardStats().then(setStats).catch(() => {});
    getFinanceOverview(now.getFullYear(), now.getMonth() + 1)
      .then(setFinance)
      .catch(() => {});
    getTrend(now.getFullYear(), now.getMonth() + 1, 6)
      .then(setTrend)
      .catch(() => {});
  }, []);

  const routineDone = routine
    ? routine.items.filter((i) => i.status !== null).length
    : 0;
  const routineTotal = routine?.items.length ?? 0;
  const routinePct = routineTotal > 0 ? Math.round((routineDone / routineTotal) * 100) : 0;

  const today = new Date().toISOString().slice(0, 10);
  const todayItem = history?.find((h) => h.challenge.date === today);
  const challengeResult = todayItem?.submissions[0]?.result ?? null;

  const currentPhase = trail?.phases.find((p) => p.is_current);
  const completedPhases = trail?.phases.filter((p) => p.completed_at !== null).length ?? 0;
  const totalPhases = trail?.phases.length ?? 6;
  const trailPct = totalPhases > 0 ? Math.round((completedPhases / totalPhases) * 100) : 0;

  const reviewDone = reviews?.reviewed_today ?? 0;
  const reviewTotal = (reviews?.reviewed_today ?? 0) + (reviews?.due ?? 0);
  const reviewPct = reviewTotal > 0 ? Math.round((reviewDone / reviewTotal) * 100) : 100;

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
        {/* Header */}
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

        {/* Summary cards */}
        <div className="grid gap-4 sm:grid-cols-2">
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

          {/* Review ("trilha de revisão") and Trail ("trilha") cards hidden for
              now — to be revisited in a dedicated issue/branch.
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
                value={reviewDone}
                total={reviewTotal}
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
          */}
        </div>

        {/* Finance overview: summary + monthly income vs spending chart */}
        <Card>
          <div className="mb-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <p className="text-xs font-bold uppercase tracking-[0.18em] text-muted">
                {t("dashboard.finance")}
              </p>
              {finance && (
                <span
                  className={`rounded-full border px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide ${
                    FINANCE_STATUS_STYLE[finance.recommendation.status]
                  }`}
                >
                  {t(`dashboard.fin_status.${finance.recommendation.status}` as TKey)}
                </span>
              )}
            </div>
            <Link
              href="/finance"
              className="text-xs font-bold text-muted underline-offset-4 transition-colors hover:text-foreground hover:underline"
            >
              {t("dashboard.see_details")}
            </Link>
          </div>
          <div className="grid gap-6 md:grid-cols-2">
            {/* Left: numbers */}
            <div className="space-y-4">
              <div>
                <p className="text-3xl font-extrabold text-rose-400">
                  {finance ? formatMoney(finance.total_spending, locale) : "—"}
                </p>
                <p className="mt-1 text-sm text-secondary">
                  {finance
                    ? `${t("dashboard.of_income")} ${formatMoney(finance.total_income, locale)}`
                    : t("dashboard.finance_sub")}
                </p>
              </div>
              <ProgressBar
                value={finance?.total_spending ?? 0}
                total={finance?.total_income ?? 0}
              />
              <div className="grid grid-cols-2 gap-3 pt-1">
                <div className="rounded-xl border border-line bg-elevated/40 p-3">
                  <p className="text-[11px] font-bold uppercase tracking-wide text-muted">
                    {t("finance.net")}
                  </p>
                  <p
                    className={`mt-1 text-lg font-extrabold ${
                      (finance?.net ?? 0) >= 0 ? "text-emerald-400" : "text-rose-400"
                    }`}
                  >
                    {finance ? formatMoney(finance.net, locale) : "—"}
                  </p>
                </div>
                <div className="rounded-xl border border-line bg-elevated/40 p-3">
                  <p className="text-[11px] font-bold uppercase tracking-wide text-muted">
                    {t("finance.savings_rate")}
                  </p>
                  <p
                    className={`mt-1 text-lg font-extrabold ${
                      (finance?.savings_rate ?? 0) >= 0.2
                        ? "text-emerald-400"
                        : "text-foreground"
                    }`}
                  >
                    {finance ? `${Math.round(finance.savings_rate * 100)}%` : "—"}
                  </p>
                </div>
              </div>
            </div>
            {/* Right: trend chart */}
            <div className="flex flex-col justify-center">
              <TrendChart points={trend} />
            </div>
          </div>
        </Card>

        {/* Progress analytics row */}
        <div className="grid gap-4 lg:grid-cols-3">
          {/* 7-day routine bars */}
          <Card className="lg:col-span-2">
            <div className="mb-4 flex items-center justify-between">
              <p className="text-xs font-bold uppercase tracking-[0.18em] text-muted">
                Routine — last 7 days
              </p>
              {stats && (
                <StreakBadge streak={stats.routine_streak} />
              )}
            </div>
            {stats ? (
              <WeekBars days={stats.routine_7d} />
            ) : (
              <div className="h-24 animate-pulse rounded-lg bg-elevated" />
            )}
          </Card>

          {/* Stat rings */}
          <Card>
            <p className="mb-4 text-xs font-bold uppercase tracking-[0.18em] text-muted">
              Completion rates
            </p>
            <div className="grid grid-cols-3 items-center gap-1">
              <StatRing
                value={routinePct}
                size={72}
                label="Routine"
                sublabel="today"
                color="rgba(255,255,255,0.85)"
              />
              <StatRing
                value={reviewPct}
                size={72}
                label="Review"
                sublabel="today"
                color="rgba(255,255,255,0.55)"
              />
              <StatRing
                value={stats?.english_accuracy_7d ?? 0}
                size={72}
                label="English"
                sublabel="7-day acc."
                color="rgba(255,255,255,0.35)"
              />
            </div>
          </Card>
        </div>

        {/* Pending today */}
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

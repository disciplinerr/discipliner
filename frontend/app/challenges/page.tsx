"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import ChallengeView from "@/components/challenge/ChallengeView";
import SubmissionForm from "@/components/challenge/SubmissionForm";
import Card from "@/components/ui/Card";
import RequireAuth from "@/components/ui/RequireAuth";
import { ApiError, getChallengeHistory, getTodayChallenge } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import { Challenge, ChallengeHistoryItem } from "@/types";

const RESULT_BADGE: Record<string, string> = {
  PASS: "bg-foreground text-background",
  FAIL: "border border-line text-red-400",
  PARTIAL: "border border-line text-secondary",
  PENDING: "border border-line text-muted",
};

export default function ChallengesPage() {
  const { t } = useI18n();
  const [challenge, setChallenge] = useState<Challenge | null>(null);
  const [history, setHistory] = useState<ChallengeHistoryItem[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    getTodayChallenge()
      .then(setChallenge)
      .catch((err) =>
        setError(err instanceof ApiError ? err.message : t("challenge.load_failed"))
      );
    getChallengeHistory().then(setHistory).catch(() => {});
  }, []);

  return (
    <RequireAuth>
      <div className="space-y-6">
        <div className="animate-fade-up">
          <h1 className="text-3xl font-extrabold tracking-tight">{t("challenge.title")}</h1>
          <p className="mt-1 text-secondary">{t("challenge.subtitle")}</p>
        </div>

        <Card>
          {error && <p className="text-sm text-red-400">{error}</p>}
          {challenge ? (
            <ChallengeView challenge={challenge} />
          ) : (
            !error && (
              <p className="text-sm text-muted">{t("challenge.generating")}</p>
            )
          )}
        </Card>

        {challenge && (
          <Card title={t("challenge.your_solution")}>
            <SubmissionForm challengeId={challenge.id} />
          </Card>
        )}

        <Card title={t("challenge.history")}>
          {history.length === 0 ? (
            <p className="text-sm text-muted">{t("challenge.none")}</p>
          ) : (
            <ul className="divide-y divide-line">
              {history.map((item) => (
                <li key={item.challenge.id}>
                  <Link
                    href={`/challenges/${item.challenge.id}`}
                    className="group flex items-center justify-between gap-4 py-3"
                  >
                    <div>
                      <p className="text-sm font-semibold transition-colors group-hover:text-foreground">
                        {item.challenge.title}
                      </p>
                      <p className="text-xs text-muted">{item.challenge.date}</p>
                    </div>
                    <span
                      className={`shrink-0 rounded-full px-2.5 py-0.5 text-xs font-bold ${
                        item.submissions[0]
                          ? RESULT_BADGE[item.submissions[0].result]
                          : "border border-dashed border-line text-muted"
                      }`}
                    >
                      {item.submissions[0]?.result ?? t("challenge.not_attempted")}
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </RequireAuth>
  );
}

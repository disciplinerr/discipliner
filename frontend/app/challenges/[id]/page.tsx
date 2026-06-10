"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import ChallengeView from "@/components/challenge/ChallengeView";
import SubmissionForm from "@/components/challenge/SubmissionForm";
import Card from "@/components/ui/Card";
import RequireAuth from "@/components/ui/RequireAuth";
import { getChallengeHistory } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import { ChallengeHistoryItem } from "@/types";

const RESULT_BADGE: Record<string, string> = {
  PASS: "bg-foreground text-background",
  FAIL: "border border-line text-red-400",
  PARTIAL: "border border-line text-secondary",
  PENDING: "border border-line text-muted",
};

export default function ChallengeDetailPage() {
  const { t, locale } = useI18n();
  const params = useParams<{ id: string }>();
  const [item, setItem] = useState<ChallengeHistoryItem | null>(null);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    getChallengeHistory()
      .then((history) => {
        const match = history.find((h) => h.challenge.id === Number(params.id));
        if (match) setItem(match);
        else setNotFound(true);
      })
      .catch(() => setNotFound(true));
  }, [params.id]);

  return (
    <RequireAuth>
      <div className="space-y-6">
        <Link
          href="/challenges"
          className="inline-block text-sm font-semibold text-muted transition-colors hover:text-foreground"
        >
          {t("common.back")}
        </Link>

        {notFound && <p className="text-sm text-red-400">{t("challenge.not_found")}</p>}

        {item && (
          <>
            <Card>
              <ChallengeView challenge={item.challenge} />
            </Card>

            <Card title={t("challenge.past_attempts")}>
              {item.submissions.length === 0 ? (
                <p className="text-sm text-muted">{t("challenge.no_attempts")}</p>
              ) : (
                <ul className="divide-y divide-line">
                  {item.submissions.map((s) => (
                    <li key={s.id} className="flex items-center gap-3 py-3">
                      <span
                        className={`shrink-0 rounded-full px-2.5 py-0.5 text-xs font-bold ${RESULT_BADGE[s.result]}`}
                      >
                        {s.result}
                      </span>
                      <div className="text-sm">
                        <p className="text-secondary">
                          {new Date(s.submitted_at).toLocaleString(locale)}
                        </p>
                        {s.reason && <p className="text-xs text-muted">{s.reason}</p>}
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </Card>

            <Card title={t("challenge.new_attempt")}>
              <SubmissionForm challengeId={item.challenge.id} />
            </Card>
          </>
        )}
      </div>
    </RequireAuth>
  );
}

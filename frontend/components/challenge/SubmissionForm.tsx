"use client";

import { FormEvent, useState } from "react";
import CodeSandbox, { Language } from "@/components/challenge/CodeSandbox";
import Button from "@/components/ui/Button";
import { ApiError, submitChallenge } from "@/lib/api";
import { TKey, useI18n } from "@/lib/i18n";
import { Submission } from "@/types";

const RESULT_BANNER: Record<string, { style: string; label: TKey }> = {
  PASS: {
    style: "border-foreground bg-foreground text-background",
    label: "challenge.result_pass",
  },
  FAIL: { style: "border-line bg-elevated text-red-400", label: "challenge.result_fail" },
  PARTIAL: {
    style: "border-line bg-elevated text-secondary",
    label: "challenge.result_partial",
  },
  PENDING: {
    style: "border-line bg-elevated text-muted",
    label: "challenge.result_pending",
  },
};

export default function SubmissionForm({ challengeId }: { challengeId: number }) {
  const { t } = useI18n();
  const [code, setCode] = useState("");
  const [language, setLanguage] = useState<Language>("python");
  const [notes, setNotes] = useState("");
  const [result, setResult] = useState<Submission | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!code.trim()) return;
    setError("");
    setResult(null);
    setBusy(true);
    try {
      setResult(await submitChallenge(challengeId, code));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("challenge.submit_failed"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* Scratch notes — local only, not submitted */}
      <div>
        <label className="mb-2 block text-xs font-bold uppercase tracking-[0.18em] text-muted">
          {t("challenge.notes_label")}
        </label>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          rows={4}
          className="w-full rounded-xl border border-line bg-elevated p-4 text-sm leading-relaxed text-foreground placeholder:text-muted transition-colors focus:border-secondary"
          placeholder={t("challenge.notes_placeholder")}
        />
      </div>

      {/* Code editor + sandbox */}
      <CodeSandbox
        code={code}
        onChange={setCode}
        language={language}
        onLanguageChange={setLanguage}
      />

      {error && <p className="text-sm text-red-400">{error}</p>}

      {result && (
        <div
          className={`animate-fade-up rounded-xl border p-4 ${RESULT_BANNER[result.result].style}`}
        >
          <p className="font-extrabold">{t(RESULT_BANNER[result.result].label)}</p>
          {result.reason && <p className="mt-1 text-sm opacity-90">{result.reason}</p>}
        </div>
      )}

      <Button type="submit" disabled={busy || !code.trim()}>
        {busy ? t("challenge.submitting") : t("challenge.submit")}
      </Button>
    </form>
  );
}

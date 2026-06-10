"use client";

import { FormEvent, useState } from "react";
import CodeSandbox from "@/components/challenge/CodeSandbox";
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
  const [derivation, setDerivation] = useState("");
  const [code, setCode] = useState("");
  const [result, setResult] = useState<Submission | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setResult(null);
    setBusy(true);
    try {
      setResult(await submitChallenge(challengeId, derivation, code));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("challenge.submit_failed"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div>
        <div className="mb-2 flex items-center justify-between">
          <label className="text-xs font-bold uppercase tracking-[0.18em] text-muted">
            {t("challenge.derivation_label")}
          </label>
          <span
            className={`text-xs font-semibold ${
              derivation.trim().length >= 50 ? "text-secondary" : "text-muted"
            }`}
          >
            {derivation.trim().length}/50 {t("challenge.derivation_min")}
          </span>
        </div>
        <textarea
          value={derivation}
          onChange={(e) => setDerivation(e.target.value)}
          rows={8}
          required
          className="w-full rounded-xl border border-line bg-elevated p-4 text-sm leading-relaxed text-foreground placeholder:text-muted transition-colors focus:border-secondary"
          placeholder={t("challenge.derivation_placeholder")}
        />
      </div>

      <div>
        <label className="mb-2 block text-xs font-bold uppercase tracking-[0.18em] text-muted">
          {t("challenge.code_label")}
        </label>
        {/* Plain textarea by design — no editor features, no autocomplete. */}
        <textarea
          value={code}
          onChange={(e) => setCode(e.target.value)}
          rows={16}
          required
          spellCheck={false}
          className="w-full rounded-xl border border-line bg-background p-4 font-mono text-sm leading-relaxed text-foreground placeholder:text-muted transition-colors focus:border-secondary"
          placeholder={t("challenge.code_placeholder")}
        />
      </div>

      <CodeSandbox code={code} />

      {error && <p className="text-sm text-red-400">{error}</p>}

      {result && (
        <div
          className={`animate-fade-up rounded-xl border p-4 ${RESULT_BANNER[result.result].style}`}
        >
          <p className="font-extrabold">{t(RESULT_BANNER[result.result].label)}</p>
          {result.reason && <p className="mt-1 text-sm opacity-90">{result.reason}</p>}
        </div>
      )}

      <Button type="submit" disabled={busy}>
        {busy ? t("challenge.submitting") : t("challenge.submit")}
      </Button>
    </form>
  );
}

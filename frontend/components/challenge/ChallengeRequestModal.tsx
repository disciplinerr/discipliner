"use client";

import { FormEvent, useState } from "react";
import ChallengeView from "@/components/challenge/ChallengeView";
import CodeSandbox, { Language } from "@/components/challenge/CodeSandbox";
import Button from "@/components/ui/Button";
import { ApiError, generateCustomChallenge } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import { PreviewChallenge } from "@/types";

interface Props {
  onClose: () => void;
}

export default function ChallengeRequestModal({ onClose }: Props) {
  const { t, locale } = useI18n();
  const [description, setDescription] = useState("");
  const [challenge, setChallenge] = useState<PreviewChallenge | null>(null);
  const [code, setCode] = useState("");
  const [language, setLanguage] = useState<Language>("python");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function handleGenerate(e: FormEvent) {
    e.preventDefault();
    if (!description.trim()) return;
    setError("");
    setChallenge(null);
    setCode("");
    setBusy(true);
    try {
      const result = await generateCustomChallenge(description.trim(), locale);
      setChallenge(result);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("challenge.modal_failed"));
    } finally {
      setBusy(false);
    }
  }

  return (
    /* Backdrop */
    <div
      className="fixed inset-0 z-50 flex items-end justify-center sm:items-center"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={onClose} />

      {/* Modal panel */}
      <div className="relative z-10 flex max-h-[92vh] w-full max-w-2xl flex-col rounded-t-2xl sm:rounded-2xl border border-line bg-background shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-line px-6 py-4 shrink-0">
          <div>
            <h2 className="text-lg font-extrabold tracking-tight">{t("challenge.modal_title")}</h2>
            <p className="text-xs text-muted">{t("challenge.modal_description")}</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg px-3 py-1.5 text-xs font-bold text-muted transition-colors hover:text-foreground hover:bg-elevated"
          >
            {t("challenge.modal_close")}
          </button>
        </div>

        {/* Scrollable body */}
        <div className="overflow-y-auto flex-1 px-6 py-5 space-y-6">
          {/* Description form */}
          <form onSubmit={handleGenerate} className="space-y-3">
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              disabled={busy}
              className="w-full rounded-xl border border-line bg-elevated p-4 text-sm leading-relaxed text-foreground placeholder:text-muted transition-colors focus:border-secondary disabled:opacity-50"
              placeholder={t("challenge.modal_placeholder")}
            />
            {error && <p className="text-sm text-red-400">{error}</p>}
            <Button type="submit" disabled={busy || !description.trim()}>
              {busy ? t("challenge.modal_generating") : t("challenge.modal_generate")}
            </Button>
          </form>

          {/* Generated challenge preview */}
          {challenge && (
            <div className="space-y-5 border-t border-line pt-5">
              {/* Custom badge */}
              <span className="inline-block rounded-full border border-line px-2.5 py-0.5 text-xs font-bold text-muted">
                {t("challenge.custom_badge")}
              </span>

              <ChallengeView challenge={challenge} />

              {/* Inline sandbox for practice */}
              <div className="space-y-3">
                <p className="text-xs font-bold uppercase tracking-[0.18em] text-muted">
                  {t("challenge.custom_practice")}
                </p>
                <CodeSandbox
                  code={code}
                  onChange={setCode}
                  language={language}
                  onLanguageChange={setLanguage}
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

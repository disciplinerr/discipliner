"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Card from "@/components/ui/Card";
import RequireAuth from "@/components/ui/RequireAuth";
import { getEnglishSession, getEnglishStats, submitEnglishAnswer } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import { EnglishExercise, EnglishSession, EnglishStats } from "@/types";

const TYPE_LABEL: Record<EnglishExercise["exercise_type"], string> = {
  multiple_choice_vocab: "english.type_multiple_choice",
  fill_in_the_blank: "english.type_fill_blank",
  translate_pt_en: "english.type_translate_pt_en",
  translate_en_pt: "english.type_translate_en_pt",
} as const;

export default function EnglishPage() {
  const { t } = useI18n();
  const [session, setSession] = useState<EnglishSession | null | "empty">(null);
  const [stats, setStats] = useState<EnglishStats | null>(null);
  const [index, setIndex] = useState(0);
  const [answer, setAnswer] = useState("");
  const [selected, setSelected] = useState<string | null>(null);
  const [result, setResult] = useState<{
    correct: boolean;
    correct_answer: string;
    session_complete: boolean;
  } | null>(null);
  const [busy, setBusy] = useState(false);
  const [correctCount, setCorrectCount] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  const load = useCallback(async () => {
    try {
      const [s, st] = await Promise.all([getEnglishSession(), getEnglishStats()]);
      setSession(s ?? "empty");
      setStats(st);
      setCorrectCount(st.done_today);
    } catch {
      setSession("empty");
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const current =
    session !== null && session !== "empty" && index < session.items.length
      ? session.items[index]
      : null;

  const isMultipleChoice = current?.exercise_type === "multiple_choice_vocab";

  async function submit() {
    if (!current || busy) return;
    const value = isMultipleChoice ? selected ?? "" : answer.trim();
    if (!value) return;
    setBusy(true);
    try {
      const res = await submitEnglishAnswer(current.item_id, current.exercise_type, value);
      if (res.correct) setCorrectCount((c) => c + 1);
      setResult(res);
    } catch {
      // silent
    } finally {
      setBusy(false);
    }
  }

  function next() {
    if (!result) return;
    if (result.session_complete) {
      // refresh stats then stay on complete screen
      getEnglishStats()
        .then(setStats)
        .catch(() => {});
      return;
    }
    setResult(null);
    setAnswer("");
    setSelected(null);
    setIndex((i) => i + 1);
    setTimeout(() => inputRef.current?.focus(), 50);
  }

  const sessionComplete = result?.session_complete ?? false;
  const allShown =
    session !== null && session !== "empty" && index >= session.items.length;

  return (
    <RequireAuth>
      <div className="space-y-6">
        <div className="animate-fade-up">
          <h1 className="text-3xl font-extrabold tracking-tight">{t("english.title")}</h1>
          <p className="mt-1 text-secondary">{t("english.subtitle")}</p>
        </div>

        {stats && (
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {[
              { label: t("english.due_today"), value: stats.due_today },
              { label: t("english.done_today"), value: correctCount },
              { label: t("english.mature"), value: stats.mature_items },
              { label: t("english.total"), value: stats.total_items },
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

        {session === null ? (
          <p className="text-sm text-muted">{t("common.loading")}</p>
        ) : sessionComplete ? (
          <Card>
            <div className="flex min-h-[200px] flex-col items-center justify-center gap-3 text-center">
              <span className="flex h-12 w-12 items-center justify-center rounded-full bg-foreground text-xl text-background">
                ✓
              </span>
              <p className="font-extrabold">{t("english.session_complete_title")}</p>
              <p className="max-w-sm text-sm text-secondary">
                {t("english.session_complete_text")}
              </p>
            </div>
          </Card>
        ) : session === "empty" || allShown ? (
          <Card>
            <div className="flex min-h-[200px] flex-col items-center justify-center gap-3 text-center">
              <p className="font-extrabold">{t("english.nothing_due")}</p>
              <p className="max-w-sm text-sm text-secondary">{t("english.nothing_due_text")}</p>
            </div>
          </Card>
        ) : current ? (
          <Card>
            <div className="flex flex-col gap-5 py-4">
              {/* Progress bar */}
              <div className="flex items-center justify-between text-xs font-semibold text-muted">
                <span>
                  {t(TYPE_LABEL[current.exercise_type] as Parameters<typeof t>[0])}
                </span>
                <span>
                  {correctCount} / 15 {t("english.session_progress").replace("of 15 correct", "").replace("de 15 corretos", "")}
                </span>
              </div>
              <div className="h-1.5 w-full rounded-full bg-elevated">
                <div
                  className="h-1.5 rounded-full bg-foreground transition-all"
                  style={{ width: `${Math.min((correctCount / 15) * 100, 100)}%` }}
                />
              </div>

              {/* Prompt */}
              <div
                className={`rounded-xl border-2 p-5 transition-colors ${
                  result
                    ? result.correct
                      ? "border-green-500/60 bg-green-500/5"
                      : "border-red-500/60 bg-red-500/5"
                    : "border-line"
                }`}
              >
                <p className="text-xl font-bold tracking-tight">{current.prompt}</p>
              </div>

              {/* Input area */}
              {!result && (
                <>
                  {isMultipleChoice && current.choices ? (
                    <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                      {current.choices.map((choice) => (
                        <button
                          key={choice}
                          onClick={() => setSelected(choice)}
                          className={`rounded-xl border p-3 text-left text-sm transition-all active:scale-[0.98] ${
                            selected === choice
                              ? "border-foreground bg-foreground text-background"
                              : "border-line text-secondary hover:border-muted hover:text-foreground"
                          }`}
                        >
                          {choice}
                        </button>
                      ))}
                    </div>
                  ) : (
                    <input
                      ref={inputRef}
                      type="text"
                      value={answer}
                      onChange={(e) => setAnswer(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && submit()}
                      placeholder={t("english.type_answer")}
                      className="w-full rounded-xl border border-line bg-surface px-4 py-3 text-sm outline-none focus:border-foreground"
                      autoComplete="off"
                      autoCorrect="off"
                      spellCheck={false}
                    />
                  )}

                  <button
                    onClick={submit}
                    disabled={busy || (isMultipleChoice ? !selected : !answer.trim())}
                    className="self-start rounded-xl bg-foreground px-6 py-2.5 text-sm font-bold text-background transition-all hover:bg-neutral-300 active:scale-[0.98] disabled:opacity-40"
                  >
                    {busy ? t("english.submitting") : t("english.submit")}
                  </button>
                </>
              )}

              {/* Result feedback */}
              {result && (
                <div className="flex flex-col gap-3">
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-sm font-bold ${result.correct ? "text-green-500" : "text-red-500"}`}
                    >
                      {result.correct ? "✓ Correto" : "✗ Incorreto"}
                    </span>
                    {!result.correct && (
                      <span className="text-sm text-muted">
                        → <span className="font-semibold text-foreground">{result.correct_answer}</span>
                      </span>
                    )}
                  </div>
                  <button
                    onClick={next}
                    className="self-start rounded-xl bg-foreground px-6 py-2.5 text-sm font-bold text-background transition-all hover:bg-neutral-300 active:scale-[0.98]"
                  >
                    Próximo →
                  </button>
                </div>
              )}
            </div>
          </Card>
        ) : null}
      </div>
    </RequireAuth>
  );
}

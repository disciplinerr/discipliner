"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import Card from "@/components/ui/Card";
import RequireAuth from "@/components/ui/RequireAuth";
import { getMe } from "@/lib/api";
import { clearTokens } from "@/lib/auth";
import { Locale, useI18n } from "@/lib/i18n";
import {
  DEFAULT_BREAK_MINUTES,
  DEFAULT_FOCUS_MINUTES,
  getPomodoroConfig,
  setPomodoroConfig,
} from "@/lib/pomodoro";
import { User } from "@/types";
import { Check } from "lucide-react";

const LOCALES: { value: Locale; label: string }[] = [
  { value: "pt-BR", label: "Português (BR)" },
  { value: "en", label: "English" },
];

export default function SettingsPage() {
  const router = useRouter();
  const { t, locale, setLocale } = useI18n();
  const [user, setUser] = useState<User | null>(null);
  const [focusMin, setFocusMin] = useState(DEFAULT_FOCUS_MINUTES);
  const [breakMin, setBreakMin] = useState(DEFAULT_BREAK_MINUTES);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    getMe().then(setUser).catch(() => {});
    const config = getPomodoroConfig();
    setFocusMin(config.focusMinutes);
    setBreakMin(config.breakMinutes);
  }, []);

  function savePomodoro(focus: number, brk: number) {
    setFocusMin(focus);
    setBreakMin(brk);
    setPomodoroConfig({ focusMinutes: focus, breakMinutes: brk });
    setSaved(true);
    setTimeout(() => setSaved(false), 1500);
  }

  return (
    <RequireAuth>
      <div className="space-y-6">
        <div className="animate-fade-up">
          <h1 className="text-3xl font-extrabold tracking-tight">
            {t("settings.title")}
          </h1>
          <p className="mt-1 text-secondary">{t("settings.subtitle")}</p>
        </div>

        <Card title={t("settings.language")}>
          <p className="mb-4 text-sm text-secondary">{t("settings.language_help")}</p>
          <div className="flex gap-2">
            {LOCALES.map((option) => (
              <button
                key={option.value}
                onClick={() => setLocale(option.value)}
                className={`rounded-xl border px-4 py-2.5 text-sm font-bold transition-all active:scale-[0.98] ${
                  locale === option.value
                    ? "border-foreground bg-foreground text-background"
                    : "border-line text-secondary hover:border-muted hover:text-foreground"
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </Card>

        <Card
          title={t("settings.pomodoro")}
          action={
            saved && (
              <span className="inline-flex items-center gap-1 text-xs font-bold text-secondary">
                {t("settings.saved")} <Check size={12} />
              </span>
            )
          }
        >
          <p className="mb-4 text-sm text-secondary">{t("settings.pomodoro_help")}</p>
          <div className="grid max-w-md grid-cols-2 gap-4">
            {[
              {
                label: t("settings.focus_minutes"),
                value: focusMin,
                min: 10,
                max: 60,
                onChange: (v: number) => savePomodoro(v, breakMin),
              },
              {
                label: t("settings.break_minutes"),
                value: breakMin,
                min: 3,
                max: 20,
                onChange: (v: number) => savePomodoro(focusMin, v),
              },
            ].map((field) => (
              <div key={field.label}>
                <label className="mb-1 block text-xs font-bold uppercase tracking-[0.18em] text-muted">
                  {field.label}
                </label>
                <input
                  type="number"
                  min={field.min}
                  max={field.max}
                  value={field.value}
                  onChange={(e) => {
                    const v = Number(e.target.value);
                    if (v >= field.min && v <= field.max) field.onChange(v);
                  }}
                  className="w-full rounded-xl border border-line bg-elevated px-4 py-2.5 text-foreground transition-colors focus:border-secondary"
                />
              </div>
            ))}
          </div>
        </Card>

        <Card title={t("settings.account")}>
          {user ? (
            <dl className="space-y-3 text-sm">
              <div className="flex justify-between border-b border-line pb-3">
                <dt className="text-muted">{t("settings.account_email")}</dt>
                <dd className="font-semibold">{user.email}</dd>
              </div>
              <div className="flex justify-between border-b border-line pb-3">
                <dt className="text-muted">{t("settings.account_since")}</dt>
                <dd className="font-semibold">
                  {new Date(user.created_at).toLocaleDateString(locale)}
                </dd>
              </div>
              <div className="flex justify-between pb-1">
                <dt className="text-muted">{t("settings.account_phase")}</dt>
                <dd className="font-semibold">{user.current_phase}/6</dd>
              </div>
            </dl>
          ) : (
            <p className="text-sm text-muted">{t("common.loading")}</p>
          )}
          <button
            onClick={() => {
              clearTokens();
              router.push("/login");
            }}
            className="mt-5 rounded-xl border border-line px-5 py-2.5 text-sm font-bold text-red-400 transition-colors hover:border-red-400"
          >
            {t("settings.logout")}
          </button>
        </Card>
      </div>
    </RequireAuth>
  );
}

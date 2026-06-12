"use client";

import { useEffect, useRef, useState } from "react";
import {
  ReminderConfig,
  checkAndFire,
  getPermission,
  getReminder,
  requestPermission,
  saveReminder,
} from "@/lib/notifications";
import { useI18n } from "@/lib/i18n";

interface Props {
  pendingCount: number;
}

export default function RoutineReminders({ pendingCount }: Props) {
  const { t, locale } = useI18n();
  const [config, setConfig] = useState<ReminderConfig>({ enabled: false, hour: 20, minute: 0 });
  const [permission, setPermission] = useState<ReturnType<typeof getPermission>>("default");
  const [saved, setSaved] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    setConfig(getReminder());
    setPermission(getPermission());
  }, []);

  // Tick every 60s to check if reminder should fire
  useEffect(() => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    if (config.enabled && permission === "granted") {
      intervalRef.current = setInterval(() => {
        checkAndFire(pendingCount, locale);
      }, 60_000);
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [config.enabled, permission, pendingCount, locale]);

  async function handlePermission() {
    const result = await requestPermission();
    setPermission(result);
  }

  function handleToggle(enabled: boolean) {
    const next = { ...config, enabled };
    setConfig(next);
    saveReminder(next);
    flashSaved();
  }

  function handleTime(value: string) {
    const [h, m] = value.split(":").map(Number);
    const next = { ...config, hour: h, minute: m };
    setConfig(next);
    saveReminder(next);
    flashSaved();
  }

  function flashSaved() {
    setSaved(true);
    setTimeout(() => setSaved(false), 1500);
  }

  const timeValue = `${String(config.hour).padStart(2, "0")}:${String(config.minute).padStart(2, "0")}`;

  return (
    <div className="space-y-4">
      {permission === "unsupported" && (
        <p className="text-xs text-muted">{t("routine.reminder_not_supported")}</p>
      )}

      {permission === "denied" && (
        <p className="text-xs text-red-400">{t("routine.reminder_permission_denied")}</p>
      )}

      {permission === "default" && (
        <button
          type="button"
          onClick={handlePermission}
          className="rounded-xl border border-line px-4 py-2 text-xs font-bold text-muted transition-colors hover:border-secondary hover:text-foreground"
        >
          {t("routine.reminder_permission_btn")}
        </button>
      )}

      {permission === "granted" && (
        <div className="space-y-3">
          {/* Enable toggle */}
          <div className="flex items-center justify-between gap-4">
            <span className="text-sm font-semibold text-foreground">
              {t("routine.reminder_enable")}
            </span>
            <button
              type="button"
              onClick={() => handleToggle(!config.enabled)}
              className={`relative h-6 w-11 rounded-full border transition-colors ${
                config.enabled
                  ? "border-foreground bg-foreground"
                  : "border-line bg-elevated"
              }`}
            >
              <span
                className={`absolute top-0.5 h-5 w-5 rounded-full bg-background transition-transform ${
                  config.enabled ? "translate-x-5" : "translate-x-0.5"
                }`}
              />
            </button>
          </div>

          {/* Time picker */}
          {config.enabled && (
            <div className="flex items-center gap-3">
              <label className="text-xs font-bold uppercase tracking-[0.18em] text-muted">
                {t("routine.reminder_time")}
              </label>
              <input
                type="time"
                value={timeValue}
                onChange={(e) => handleTime(e.target.value)}
                className="rounded-lg border border-line bg-elevated px-3 py-1.5 text-sm font-semibold text-foreground focus:border-secondary focus:outline-none"
              />
              {saved && (
                <span className="text-xs font-bold text-secondary">
                  {t("routine.reminder_saved")}
                </span>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

"use client";

import { useState } from "react";
import { ApiError, checkRoutineItem } from "@/lib/api";
import { routineLabel, useI18n } from "@/lib/i18n";
import { RoutineItem } from "@/types";
import { Check } from "lucide-react";

export default function RoutineChecklist({
  items,
  onChange,
}: {
  items: RoutineItem[];
  onChange: () => void;
}) {
  const { t, locale } = useI18n();
  const [error, setError] = useState("");
  const [pending, setPending] = useState<string | null>(null);

  async function check(itemKey: string, status: "DONE" | "SKIPPED") {
    setError("");
    setPending(itemKey);
    try {
      await checkRoutineItem(itemKey, status);
      onChange();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("routine.log_failed"));
    } finally {
      setPending(null);
    }
  }

  return (
    <div>
      <ul className="divide-y divide-line">
        {items.map((item) => {
          const logged = item.status !== null;
          return (
            <li
              key={item.item_key}
              className="flex items-center justify-between gap-4 py-3.5"
            >
              <div className="flex items-center gap-3">
                <span
                  className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-lg border text-xs font-bold transition-colors ${
                    item.status === "DONE"
                      ? "border-foreground bg-foreground text-background"
                      : item.status === "LATE"
                        ? "border-secondary text-secondary"
                        : item.status === "SKIPPED"
                          ? "border-line text-muted"
                          : "border-line"
                  }`}
                >
                  {item.status === "DONE" && <Check size={14} />}
                  {item.status === "LATE" && "!"}
                  {item.status === "SKIPPED" && "–"}
                </span>
                <div>
                  <p
                    className={`text-sm font-semibold ${
                      logged ? "text-secondary" : "text-foreground"
                    }`}
                  >
                    {routineLabel(t, item.item_key, item.label)}
                  </p>
                  {item.logged_at && (
                    <p className="text-xs text-muted">
                      {item.status === "DONE"
                        ? t("routine.legend_done")
                        : item.status === "LATE"
                          ? t("routine.legend_late")
                          : t("routine.legend_skipped")}{" "}
                      ·{" "}
                      {new Date(item.logged_at).toLocaleTimeString(locale, {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </p>
                  )}
                </div>
              </div>

              {!logged && (
                <div className="flex shrink-0 gap-2">
                  <button
                    onClick={() => check(item.item_key, "DONE")}
                    disabled={pending === item.item_key}
                    className="rounded-full bg-foreground px-3.5 py-1.5 text-xs font-bold text-background transition-all hover:bg-neutral-300 active:scale-95 disabled:opacity-40"
                  >
                    {t("routine.done")}
                  </button>
                  <button
                    onClick={() => check(item.item_key, "SKIPPED")}
                    disabled={pending === item.item_key}
                    className="rounded-full border border-line px-3.5 py-1.5 text-xs font-bold text-muted transition-colors hover:border-muted hover:text-secondary disabled:opacity-40"
                  >
                    {t("routine.skip")}
                  </button>
                </div>
              )}
            </li>
          );
        })}
      </ul>
      {error && <p className="mt-3 text-sm text-red-400">{error}</p>}
    </div>
  );
}

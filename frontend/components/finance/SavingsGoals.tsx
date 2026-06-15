"use client";

import { useState } from "react";
import { SavingsGoal } from "@/types";
import { useI18n } from "@/lib/i18n";
import { formatMoney, pct } from "@/lib/finance";
import { contributeGoal, deleteGoal } from "@/lib/api";

interface Props {
  goals: SavingsGoal[];
  onChanged: () => void;
}

export default function SavingsGoals({ goals, onChanged }: Props) {
  const { t, locale } = useI18n();
  const [busy, setBusy] = useState<number | null>(null);
  const [amounts, setAmounts] = useState<Record<number, string>>({});

  if (goals.length === 0) {
    return <p className="text-sm text-muted">{t("finance.no_goals")}</p>;
  }

  const contribute = async (id: number) => {
    const raw = amounts[id];
    const value = parseFloat((raw ?? "").replace(",", "."));
    if (!(value > 0)) return;
    setBusy(id);
    try {
      await contributeGoal(id, value);
      setAmounts((a) => ({ ...a, [id]: "" }));
      onChanged();
    } finally {
      setBusy(null);
    }
  };

  const remove = async (id: number) => {
    setBusy(id);
    try {
      await deleteGoal(id);
      onChanged();
    } finally {
      setBusy(null);
    }
  };

  return (
    <div className="space-y-4">
      {goals.map((g) => {
        const ratio = pct(g.current_amount, g.target_amount);
        const done = g.current_amount >= g.target_amount;
        return (
          <div key={g.id} className="rounded-xl border border-line bg-surface p-4">
            <div className="mb-1 flex items-baseline justify-between text-sm">
              <span className="font-semibold">
                <span className="mr-1.5">{g.emoji}</span>
                {g.name}
                {done && (
                  <span className="ml-2 text-xs font-bold text-emerald-400">
                    {t("finance.goal_reached")}
                  </span>
                )}
              </span>
              <span className="text-secondary">
                {formatMoney(g.current_amount, locale)}
                <span className="text-muted">
                  {" "}
                  {t("finance.budget_of")} {formatMoney(g.target_amount, locale)}
                </span>
              </span>
            </div>
            <div className="h-2 w-full overflow-hidden rounded-full bg-elevated">
              <div
                className="h-full rounded-full transition-all duration-500"
                style={{ width: `${ratio}%`, backgroundColor: done ? "#4ade80" : g.color }}
              />
            </div>
            <div className="mt-3 flex items-center gap-2">
              <input
                inputMode="decimal"
                value={amounts[g.id] ?? ""}
                onChange={(e) => setAmounts((a) => ({ ...a, [g.id]: e.target.value }))}
                placeholder={t("finance.goal_contribute_ph")}
                className="w-28 rounded-lg border border-line bg-elevated px-3 py-1.5 text-sm text-foreground transition-colors focus:border-secondary"
              />
              <button
                type="button"
                disabled={busy === g.id}
                onClick={() => contribute(g.id)}
                className="rounded-lg border border-emerald-500/40 px-2.5 py-1.5 text-[11px] font-bold text-emerald-400 transition-colors hover:bg-emerald-500/10 disabled:opacity-40"
              >
                {t("finance.goal_contribute")}
              </button>
              <button
                type="button"
                disabled={busy === g.id}
                onClick={() => remove(g.id)}
                aria-label={t("finance.form.delete")}
                className="ml-auto rounded-lg px-2 py-1.5 text-[11px] font-bold text-muted transition-colors hover:text-rose-400 disabled:opacity-40"
              >
                ✕
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}

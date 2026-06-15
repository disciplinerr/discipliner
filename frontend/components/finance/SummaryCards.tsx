"use client";

import { FinanceOverview } from "@/types";
import { useI18n } from "@/lib/i18n";
import { formatMoney } from "@/lib/finance";

export default function SummaryCards({ data }: { data: FinanceOverview }) {
  const { t, locale } = useI18n();
  const positive = data.balance >= 0;

  const cells = [
    {
      label: t("finance.income"),
      value: formatMoney(data.income, locale),
      tone: "text-emerald-400",
    },
    {
      label: t("finance.expense"),
      value: formatMoney(data.expense, locale),
      tone: "text-rose-400",
    },
    {
      label: t("finance.balance"),
      value: formatMoney(data.balance, locale),
      tone: positive ? "text-foreground" : "text-rose-400",
    },
    {
      label: t("finance.savings_rate"),
      value: `${Math.round(data.savings_rate * 100)}%`,
      tone: data.savings_rate >= 0.2 ? "text-emerald-400" : "text-secondary",
    },
  ];

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      {cells.map((c) => (
        <div
          key={c.label}
          className="animate-fade-up rounded-2xl border border-line bg-surface p-4 shadow-soft"
        >
          <p className="text-[11px] font-bold uppercase tracking-[0.14em] text-muted">
            {c.label}
          </p>
          <p className={`mt-1 text-lg font-extrabold tracking-tight ${c.tone}`}>{c.value}</p>
        </div>
      ))}
    </div>
  );
}

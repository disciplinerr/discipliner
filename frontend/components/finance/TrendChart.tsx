"use client";

import { TrendPoint } from "@/types";
import { useI18n } from "@/lib/i18n";
import { formatMoney } from "@/lib/finance";

export default function TrendChart({ points }: { points: TrendPoint[] }) {
  const { t, locale } = useI18n();

  if (points.length === 0) {
    return <p className="text-sm text-muted">{t("finance.no_trend")}</p>;
  }

  // Shared scale across both series so bar heights are comparable month to month.
  const max = Math.max(1, ...points.map((p) => Math.max(p.income, p.expense)));

  const monthLabel = (p: TrendPoint) =>
    new Date(p.year, p.month - 1, 1).toLocaleDateString(
      locale === "pt-BR" ? "pt-BR" : "en-US",
      { month: "short" },
    );

  return (
    <div>
      <div className="flex items-end justify-between gap-2 sm:gap-3">
        {points.map((p) => (
          <div key={`${p.year}-${p.month}`} className="flex flex-1 flex-col items-center gap-1">
            <div className="flex h-28 w-full items-end justify-center gap-1">
              <div
                className="w-1/2 max-w-[14px] rounded-t bg-emerald-400/80 transition-all duration-500"
                style={{ height: `${(p.income / max) * 100}%` }}
                title={`${t("finance.income")}: ${formatMoney(p.income, locale)}`}
              />
              <div
                className="w-1/2 max-w-[14px] rounded-t bg-rose-400/80 transition-all duration-500"
                style={{ height: `${(p.expense / max) * 100}%` }}
                title={`${t("finance.expense")}: ${formatMoney(p.expense, locale)}`}
              />
            </div>
            <span className="text-[10px] font-semibold capitalize text-muted">
              {monthLabel(p)}
            </span>
          </div>
        ))}
      </div>
      <div className="mt-3 flex items-center justify-center gap-4 text-[11px] text-muted">
        <span className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-emerald-400/80" /> {t("finance.income")}
        </span>
        <span className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-rose-400/80" /> {t("finance.expense")}
        </span>
      </div>
    </div>
  );
}

"use client";

import { Recommendation } from "@/types";
import { TKey as I18nKey, useI18n } from "@/lib/i18n";
import { formatMoney } from "@/lib/finance";
import AppIcon from "@/lib/icons";

const STATUS_STYLE: Record<string, string> = {
  healthy: "border-emerald-500/40 bg-emerald-500/5 text-emerald-400",
  tight: "border-amber-500/40 bg-amber-500/5 text-amber-400",
  over: "border-rose-500/40 bg-rose-500/5 text-rose-400",
  unknown: "border-line bg-elevated/40 text-muted",
};

// recommendation area key -> app icon key
const GUIDELINE_ICON: Record<string, string> = {
  housing: "housing",
  food: "groceries",
  transport: "transport",
  leisure: "leisure",
  shopping: "shopping",
  education: "education",
  savings: "savings",
  debt: "debt",
};

export default function SpendingRecommendation({ data }: { data: Recommendation }) {
  const { t, locale } = useI18n();

  return (
    <div className="space-y-4">
      <p className="text-xs text-muted">{t("finance.recommendation_help")}</p>

      <div
        className={`rounded-xl border px-4 py-3 text-sm font-semibold ${
          STATUS_STYLE[data.status] ?? STATUS_STYLE.unknown
        }`}
      >
        {t(`finance.status.${data.status}` as I18nKey)}
        {data.status !== "unknown" && (
          <span className="ml-1 font-bold">
            {t("finance.status_leftover")} {formatMoney(data.leftover, locale)} (
            {Math.round(data.savings_rate * 100)}%)
          </span>
        )}
      </div>

      {/* 50/30/20 recommended caps */}
      <div className="grid grid-cols-3 gap-2">
        {data.groups.map((g) => (
          <div key={g.group} className="rounded-xl border border-line bg-surface p-3 text-center">
            <p className="text-[11px] font-bold uppercase tracking-wide text-muted">
              {t(`finance.group.${g.group}` as I18nKey)} {g.pct}%
            </p>
            <p className="mt-1 text-sm font-extrabold">{formatMoney(g.amount, locale)}</p>
          </div>
        ))}
      </div>

      {/* Per-area breakdown */}
      <ul className="space-y-1.5">
        {data.items.map((it) => (
          <li
            key={it.key}
            className="flex items-center justify-between gap-3 rounded-lg px-1 py-1 text-sm"
          >
            <span className="flex items-center gap-2 text-secondary">
              <AppIcon name={GUIDELINE_ICON[it.key] ?? "tag"} size={15} />
              {t(`finance.guideline.${it.key}` as I18nKey)}
              <span className="text-[11px] font-semibold text-muted">{it.pct}%</span>
            </span>
            <span className="font-bold">{formatMoney(it.amount, locale)}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

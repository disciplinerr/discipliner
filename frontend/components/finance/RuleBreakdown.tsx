"use client";

import { GroupSpend } from "@/types";
import { TKey as I18nKey, useI18n } from "@/lib/i18n";
import { formatMoney, pct } from "@/lib/finance";

const GROUP_COLOR: Record<string, string> = {
  NEEDS: "#60a5fa",
  WANTS: "#a78bfa",
  SAVINGS: "#4ade80",
};

export default function RuleBreakdown({
  groups,
  income,
}: {
  groups: GroupSpend[];
  income: number;
}) {
  const { t, locale } = useI18n();

  return (
    <div className="space-y-4">
      <p className="text-xs text-muted">{t("finance.rule_503020_help")}</p>
      {groups.map((g) => {
        // Recommended cap for this group from income (50/30/20), and the bar
        // measures spending against that cap so the user sees if they overshot.
        const cap = (income * g.target_pct) / 100;
        const ratio = pct(g.spent, cap);
        const over = cap > 0 && g.spent > cap;
        return (
          <div key={g.group}>
            <div className="mb-1 flex items-baseline justify-between text-sm">
              <span className="font-bold">
                {t(`finance.group.${g.group}` as I18nKey)}
                <span className="ml-2 text-xs font-semibold text-muted">{g.target_pct}%</span>
              </span>
              <span className={over ? "font-bold text-rose-400" : "text-secondary"}>
                {formatMoney(g.spent, locale)}
                {cap > 0 && (
                  <span className="text-muted"> / {formatMoney(cap, locale)}</span>
                )}
              </span>
            </div>
            <div className="h-2 w-full overflow-hidden rounded-full bg-elevated">
              <div
                className="h-full rounded-full transition-all duration-500"
                style={{
                  width: `${ratio}%`,
                  backgroundColor: over ? "#fb7185" : GROUP_COLOR[g.group],
                }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

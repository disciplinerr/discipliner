"use client";

import { CategorySpend } from "@/types";
import { useI18n } from "@/lib/i18n";
import { formatMoney, pct } from "@/lib/finance";

export default function CategoryBudgets({ categories }: { categories: CategorySpend[] }) {
  const { t, locale } = useI18n();

  // Only show categories that have either a budget or some spending this month.
  const rows = categories.filter((c) => c.budget > 0 || c.spent > 0);

  if (rows.length === 0) {
    return <p className="text-sm text-muted">{t("finance.no_budget")}</p>;
  }

  return (
    <div className="space-y-4">
      {rows.map((c) => {
        const ratio = pct(c.spent, c.budget);
        const over = c.budget > 0 && c.spent > c.budget;
        return (
          <div key={c.category_id}>
            <div className="mb-1 flex items-baseline justify-between text-sm">
              <span className="font-semibold">
                <span className="mr-1.5">{c.emoji}</span>
                {c.name}
              </span>
              <span className={over ? "font-bold text-rose-400" : "text-secondary"}>
                {formatMoney(c.spent, locale)}
                {c.budget > 0 ? (
                  <span className="text-muted">
                    {" "}
                    {t("finance.budget_of")} {formatMoney(c.budget, locale)}
                  </span>
                ) : (
                  <span className="text-muted"> · {t("finance.no_budget")}</span>
                )}
              </span>
            </div>
            <div className="h-2 w-full overflow-hidden rounded-full bg-elevated">
              <div
                className="h-full rounded-full transition-all duration-500"
                style={{
                  width: `${c.budget > 0 ? ratio : 0}%`,
                  backgroundColor: over ? "#fb7185" : c.color,
                }}
              />
            </div>
            {over && (
              <p className="mt-1 text-[11px] font-semibold text-rose-400">
                {t("finance.over_budget")}
              </p>
            )}
          </div>
        );
      })}
    </div>
  );
}

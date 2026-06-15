"use client";

import { useState } from "react";
import { RecurringIncome } from "@/types";
import { TKey as I18nKey, useI18n } from "@/lib/i18n";
import { formatMoney } from "@/lib/finance";
import { deleteIncome } from "@/lib/api";
import { X } from "lucide-react";

interface Props {
  incomes: RecurringIncome[];
  onChanged: () => void;
}

const KIND_BADGE: Record<string, string> = {
  SALARY: "border-emerald-500/40 text-emerald-400",
  BENEFIT: "border-sky-500/40 text-sky-400",
  OTHER: "border-line text-muted",
};

export default function IncomeList({ incomes, onChanged }: Props) {
  const { t, locale } = useI18n();
  const [busy, setBusy] = useState<number | null>(null);

  if (incomes.length === 0) {
    return <p className="text-sm text-muted">{t("finance.no_incomes")}</p>;
  }

  const remove = async (id: number) => {
    setBusy(id);
    try {
      await deleteIncome(id);
      onChanged();
    } finally {
      setBusy(null);
    }
  };

  return (
    <ul className="space-y-2">
      {incomes.map((i) => (
        <li
          key={i.id}
          className="flex items-center justify-between gap-3 rounded-xl border border-line bg-surface px-4 py-3"
        >
          <div className="min-w-0">
            <p className="truncate font-semibold">{i.name}</p>
            <span
              className={`mt-1 inline-block rounded-md border px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wide ${
                KIND_BADGE[i.kind] ?? KIND_BADGE.OTHER
              }`}
            >
              {t(`finance.income_kind.${i.kind}` as I18nKey)}
            </span>
          </div>
          <div className="flex shrink-0 items-center gap-2">
            <span className="text-sm font-bold text-emerald-400">
              {formatMoney(i.amount, locale)}
            </span>
            <button
              type="button"
              disabled={busy === i.id}
              onClick={() => remove(i.id)}
              aria-label={t("finance.form.delete")}
              className="rounded-lg px-2 py-1 text-muted transition-colors hover:text-rose-400 disabled:opacity-40"
            >
              <X size={14} />
            </button>
          </div>
        </li>
      ))}
    </ul>
  );
}

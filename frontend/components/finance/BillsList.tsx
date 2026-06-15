"use client";

import { useState } from "react";
import { BillStatus } from "@/types";
import { useI18n } from "@/lib/i18n";
import { formatMoney } from "@/lib/finance";
import { deleteBill, payBill, unpayBill } from "@/lib/api";
import { X } from "lucide-react";

interface Props {
  bills: BillStatus[];
  year: number;
  month: number;
  onChanged: () => void;
}

export default function BillsList({ bills, year, month, onChanged }: Props) {
  const { t, locale } = useI18n();
  const [busy, setBusy] = useState<number | null>(null);

  if (bills.length === 0) {
    return <p className="text-sm text-muted">{t("finance.no_bills")}</p>;
  }

  const toggle = async (b: BillStatus) => {
    setBusy(b.id);
    try {
      if (b.paid) await unpayBill(b.id, year, month);
      else await payBill(b.id, year, month);
      onChanged();
    } finally {
      setBusy(null);
    }
  };

  const remove = async (id: number) => {
    setBusy(id);
    try {
      await deleteBill(id);
      onChanged();
    } finally {
      setBusy(null);
    }
  };

  return (
    <ul className="space-y-2">
      {bills.map((b) => (
        <li
          key={b.id}
          className={`flex items-center justify-between gap-3 rounded-xl border px-4 py-3 transition-colors ${
            b.paid
              ? "border-line bg-elevated/40"
              : b.overdue
                ? "border-rose-500/40 bg-rose-500/5"
                : "border-line bg-surface"
          }`}
        >
          <div className="min-w-0">
            <p className={`truncate font-semibold ${b.paid ? "text-muted line-through" : ""}`}>
              {b.name}
            </p>
            <p className="text-xs text-muted">
              {t("finance.due_day")} {b.due_day}
              {b.overdue && !b.paid && (
                <span className="ml-2 font-bold text-rose-400">{t("finance.overdue")}</span>
              )}
              {b.paid && (
                <span className="ml-2 font-bold text-emerald-400">{t("finance.paid")}</span>
              )}
            </p>
          </div>
          <div className="flex shrink-0 items-center gap-2">
            <span className="text-sm font-bold">{formatMoney(b.amount, locale)}</span>
            <button
              type="button"
              disabled={busy === b.id}
              onClick={() => toggle(b)}
              className={`rounded-lg border px-2.5 py-1 text-[11px] font-bold transition-colors disabled:opacity-40 ${
                b.paid
                  ? "border-line text-muted hover:text-foreground"
                  : "border-emerald-500/40 text-emerald-400 hover:bg-emerald-500/10"
              }`}
            >
              {b.paid ? t("finance.mark_unpaid") : t("finance.mark_paid")}
            </button>
            <button
              type="button"
              disabled={busy === b.id}
              onClick={() => remove(b.id)}
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

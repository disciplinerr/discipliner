"use client";

import { useState } from "react";
import { InstallmentStatus } from "@/types";
import { useI18n } from "@/lib/i18n";
import { formatMoney } from "@/lib/finance";
import { deleteInstallment } from "@/lib/api";

interface Props {
  installments: InstallmentStatus[];
  onChanged: () => void;
}

export default function InstallmentsList({ installments, onChanged }: Props) {
  const { t, locale } = useI18n();
  const [busy, setBusy] = useState<number | null>(null);

  if (installments.length === 0) {
    return <p className="text-sm text-muted">{t("finance.no_installments")}</p>;
  }

  const remove = async (id: number) => {
    setBusy(id);
    try {
      await deleteInstallment(id);
      onChanged();
    } finally {
      setBusy(null);
    }
  };

  const endLabel = (i: InstallmentStatus) =>
    new Date(i.end_year, i.end_month - 1, 1).toLocaleDateString(
      locale === "pt-BR" ? "pt-BR" : "en-US",
      { month: "short", year: "numeric" },
    );

  return (
    <ul className="space-y-2">
      {installments.map((i) => {
        const last = i.remaining_count === 1;
        return (
          <li
            key={i.id}
            className="flex items-center justify-between gap-3 rounded-xl border border-line bg-surface px-4 py-3"
          >
            <div className="min-w-0">
              <p className="truncate font-semibold">{i.description}</p>
              <p className="text-xs text-muted">
                <span className="font-bold text-foreground">
                  {i.number}/{i.total_installments}
                </span>{" "}
                · {t("finance.installment_ends")} {endLabel(i)}
                {last && (
                  <span className="ml-2 font-bold text-emerald-400">
                    {t("finance.installment_last")}
                  </span>
                )}
              </p>
            </div>
            <div className="flex shrink-0 items-center gap-3">
              <div className="text-right">
                <p className="text-sm font-bold">
                  {formatMoney(i.installment_amount, locale)}
                </p>
                <p className="text-[11px] text-muted">
                  {t("finance.installment_remaining")} {formatMoney(i.remaining_amount, locale)}
                </p>
              </div>
              <button
                type="button"
                disabled={busy === i.id}
                onClick={() => remove(i.id)}
                aria-label={t("finance.form.delete")}
                className="rounded-lg px-2 py-1 text-[11px] font-bold text-muted transition-colors hover:text-rose-400 disabled:opacity-40"
              >
                ✕
              </button>
            </div>
          </li>
        );
      })}
    </ul>
  );
}

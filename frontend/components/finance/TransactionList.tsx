"use client";

import { useState } from "react";
import { Category, Transaction } from "@/types";
import { useI18n } from "@/lib/i18n";
import { formatMoney } from "@/lib/finance";
import { deleteTransaction } from "@/lib/api";
import AppIcon from "@/lib/icons";
import { X } from "lucide-react";

interface Props {
  transactions: Transaction[];
  categories: Category[];
  onChanged: () => void;
}

export default function TransactionList({ transactions, categories, onChanged }: Props) {
  const { t, locale } = useI18n();
  const [busy, setBusy] = useState<number | null>(null);

  if (transactions.length === 0) {
    return <p className="text-sm text-muted">{t("finance.no_transactions")}</p>;
  }

  const catById = new Map(categories.map((c) => [c.id, c]));

  const remove = async (id: number) => {
    setBusy(id);
    try {
      await deleteTransaction(id);
      onChanged();
    } finally {
      setBusy(null);
    }
  };

  const fmtDate = (iso: string) =>
    new Date(iso + "T00:00:00").toLocaleDateString(locale === "pt-BR" ? "pt-BR" : "en-US", {
      day: "2-digit",
      month: "short",
    });

  return (
    <ul className="divide-y divide-line">
      {transactions.map((tx) => {
        const cat = tx.category_id != null ? catById.get(tx.category_id) : undefined;
        const income = tx.kind === "INCOME";
        return (
          <li key={tx.id} className="flex items-center justify-between gap-3 py-3">
            <div className="flex min-w-0 items-center gap-3">
              <AppIcon
                name={cat?.emoji ?? (income ? "money" : "tag")}
                size={20}
                color={cat?.color ?? (income ? "#34d399" : undefined)}
              />
              <div className="min-w-0">
                <p className="truncate font-semibold">{tx.description}</p>
                <p className="text-xs text-muted">
                  {fmtDate(tx.date)} · {cat?.name ?? t("finance.uncategorized")}
                </p>
              </div>
            </div>
            <div className="flex shrink-0 items-center gap-3">
              <span
                className={`text-sm font-bold ${income ? "text-emerald-400" : "text-foreground"}`}
              >
                {income ? "+" : "−"}
                {formatMoney(tx.amount, locale)}
              </span>
              <button
                type="button"
                disabled={busy === tx.id}
                onClick={() => remove(tx.id)}
                aria-label={t("finance.form.delete")}
                className="rounded-lg px-2 py-1 text-muted transition-colors hover:text-rose-400 disabled:opacity-40"
              >
                <X size={14} />
              </button>
            </div>
          </li>
        );
      })}
    </ul>
  );
}

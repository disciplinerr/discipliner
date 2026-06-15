"use client";

import { useState } from "react";
import { Category } from "@/types";
import { useI18n } from "@/lib/i18n";
import { createTransaction } from "@/lib/api";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Modal from "./Modal";

interface Props {
  categories: Category[];
  defaultDate: string; // yyyy-mm-dd within the selected month
  onClose: () => void;
  onSaved: () => void;
}

const fieldLabel = "mb-1 block text-xs font-bold uppercase tracking-wide text-muted";

export default function AddTransactionModal({
  categories,
  defaultDate,
  onClose,
  onSaved,
}: Props) {
  const { t } = useI18n();
  const [kind, setKind] = useState<"EXPENSE" | "INCOME">("EXPENSE");
  const [description, setDescription] = useState("");
  const [amount, setAmount] = useState("");
  const [date, setDate] = useState(defaultDate);
  const [categoryId, setCategoryId] = useState<string>("");
  const [busy, setBusy] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    const value = parseFloat(amount.replace(",", "."));
    if (!description.trim() || !(value > 0)) return;
    setBusy(true);
    try {
      await createTransaction({
        description: description.trim(),
        amount: value,
        kind,
        date,
        category_id: kind === "EXPENSE" && categoryId ? Number(categoryId) : null,
      });
      onSaved();
      onClose();
    } finally {
      setBusy(false);
    }
  };

  return (
    <Modal title={t("finance.new_transaction")} onClose={onClose}>
      <form onSubmit={submit} className="space-y-4">
        {/* Kind toggle */}
        <div className="grid grid-cols-2 gap-2">
          {(["EXPENSE", "INCOME"] as const).map((k) => (
            <button
              key={k}
              type="button"
              onClick={() => setKind(k)}
              className={`rounded-xl border px-4 py-2.5 text-sm font-bold transition-colors ${
                kind === k
                  ? k === "INCOME"
                    ? "border-emerald-500/50 bg-emerald-500/10 text-emerald-400"
                    : "border-rose-500/50 bg-rose-500/10 text-rose-400"
                  : "border-line text-secondary hover:text-foreground"
              }`}
            >
              {k === "INCOME" ? t("finance.income") : t("finance.expense")}
            </button>
          ))}
        </div>

        <div>
          <label className={fieldLabel}>{t("finance.form.description")}</label>
          <Input value={description} onChange={(e) => setDescription(e.target.value)} autoFocus />
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className={fieldLabel}>{t("finance.form.amount")}</label>
            <Input
              inputMode="decimal"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="0,00"
            />
          </div>
          <div>
            <label className={fieldLabel}>{t("finance.form.date")}</label>
            <Input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
          </div>
        </div>

        {kind === "EXPENSE" && (
          <div>
            <label className={fieldLabel}>{t("finance.form.category")}</label>
            <select
              value={categoryId}
              onChange={(e) => setCategoryId(e.target.value)}
              className="w-full rounded-xl border border-line bg-elevated px-4 py-2.5 text-foreground transition-colors focus:border-secondary"
            >
              <option value="">{t("finance.uncategorized")}</option>
              {categories
                .filter((c) => c.is_active)
                .map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.emoji} {c.name}
                  </option>
                ))}
            </select>
          </div>
        )}

        <div className="flex gap-2 pt-2">
          <Button type="submit" disabled={busy} className="flex-1">
            {t("finance.form.save")}
          </Button>
          <Button type="button" variant="ghost" onClick={onClose}>
            {t("finance.form.cancel")}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

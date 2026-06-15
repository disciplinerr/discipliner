"use client";

import { useState } from "react";
import { Category } from "@/types";
import { useI18n } from "@/lib/i18n";
import { formatMoney } from "@/lib/finance";
import { createInstallment } from "@/lib/api";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Modal from "./Modal";

interface Props {
  categories: Category[];
  defaultYear: number;
  defaultMonth: number;
  onClose: () => void;
  onSaved: () => void;
}

const fieldLabel = "mb-1 block text-xs font-bold uppercase tracking-wide text-muted";
const selectCls =
  "w-full rounded-xl border border-line bg-elevated px-4 py-2.5 text-foreground transition-colors focus:border-secondary";

export default function AddInstallmentModal({
  categories,
  defaultYear,
  defaultMonth,
  onClose,
  onSaved,
}: Props) {
  const { t, locale } = useI18n();
  const [description, setDescription] = useState("");
  const [amount, setAmount] = useState("");
  const [count, setCount] = useState("12");
  const [startYear, setStartYear] = useState(String(defaultYear));
  const [startMonth, setStartMonth] = useState(String(defaultMonth));
  const [dueDay, setDueDay] = useState("1");
  const [categoryId, setCategoryId] = useState<string>("");
  const [busy, setBusy] = useState(false);

  const value = parseFloat(amount.replace(",", "."));
  const n = parseInt(count, 10);
  // Live preview of the full purchase cost so the user sees the commitment.
  const total = value > 0 && n > 0 ? value * n : 0;

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    const day = parseInt(dueDay, 10);
    if (!description.trim() || !(value > 0) || !(n >= 1)) return;
    setBusy(true);
    try {
      await createInstallment({
        description: description.trim(),
        installment_amount: value,
        total_installments: n,
        start_year: parseInt(startYear, 10),
        start_month: parseInt(startMonth, 10),
        due_day: day >= 1 && day <= 31 ? day : 1,
        category_id: categoryId ? Number(categoryId) : null,
      });
      onSaved();
      onClose();
    } finally {
      setBusy(false);
    }
  };

  const months = Array.from({ length: 12 }, (_, i) => i + 1);

  return (
    <Modal title={t("finance.new_installment")} onClose={onClose}>
      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className={fieldLabel}>{t("finance.form.description")}</label>
          <Input
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            autoFocus
          />
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className={fieldLabel}>{t("finance.form.installment_amount")}</label>
            <Input
              inputMode="decimal"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="0,00"
            />
          </div>
          <div>
            <label className={fieldLabel}>{t("finance.form.installments")}</label>
            <Input
              type="number"
              min={1}
              max={360}
              value={count}
              onChange={(e) => setCount(e.target.value)}
            />
          </div>
        </div>

        <div className="grid grid-cols-3 gap-3">
          <div>
            <label className={fieldLabel}>{t("finance.form.start_month")}</label>
            <select
              value={startMonth}
              onChange={(e) => setStartMonth(e.target.value)}
              className={selectCls}
            >
              {months.map((m) => (
                <option key={m} value={m}>
                  {new Date(2000, m - 1, 1).toLocaleDateString(
                    locale === "pt-BR" ? "pt-BR" : "en-US",
                    { month: "short" },
                  )}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={fieldLabel}>{t("finance.form.start_year")}</label>
            <Input
              type="number"
              min={2020}
              max={2100}
              value={startYear}
              onChange={(e) => setStartYear(e.target.value)}
            />
          </div>
          <div>
            <label className={fieldLabel}>{t("finance.form.due_day")}</label>
            <Input
              type="number"
              min={1}
              max={31}
              value={dueDay}
              onChange={(e) => setDueDay(e.target.value)}
            />
          </div>
        </div>

        <div>
          <label className={fieldLabel}>{t("finance.form.category")}</label>
          <select
            value={categoryId}
            onChange={(e) => setCategoryId(e.target.value)}
            className={selectCls}
          >
            <option value="">{t("finance.uncategorized")}</option>
            {categories
              .filter((c) => c.is_active)
              .map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
          </select>
        </div>

        {total > 0 && (
          <p className="rounded-xl border border-line bg-elevated/40 px-4 py-2.5 text-sm text-secondary">
            {t("finance.installment_total_preview")}{" "}
            <span className="font-bold text-foreground">{formatMoney(total, locale)}</span>{" "}
            ({n}× {formatMoney(value, locale)})
          </p>
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

"use client";

import { useState } from "react";
import { Category } from "@/types";
import { useI18n } from "@/lib/i18n";
import { createBill } from "@/lib/api";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Modal from "./Modal";

interface Props {
  categories: Category[];
  onClose: () => void;
  onSaved: () => void;
}

const fieldLabel = "mb-1 block text-xs font-bold uppercase tracking-wide text-muted";

export default function AddBillModal({ categories, onClose, onSaved }: Props) {
  const { t } = useI18n();
  const [name, setName] = useState("");
  const [amount, setAmount] = useState("");
  const [dueDay, setDueDay] = useState("1");
  const [categoryId, setCategoryId] = useState<string>("");
  const [busy, setBusy] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    const value = parseFloat(amount.replace(",", "."));
    const day = parseInt(dueDay, 10);
    if (!name.trim() || !(value > 0) || !(day >= 1 && day <= 31)) return;
    setBusy(true);
    try {
      await createBill({
        name: name.trim(),
        amount: value,
        due_day: day,
        category_id: categoryId ? Number(categoryId) : null,
      });
      onSaved();
      onClose();
    } finally {
      setBusy(false);
    }
  };

  return (
    <Modal title={t("finance.new_bill")} onClose={onClose}>
      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className={fieldLabel}>{t("finance.form.name")}</label>
          <Input value={name} onChange={(e) => setName(e.target.value)} autoFocus />
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

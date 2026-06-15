"use client";

import { useState } from "react";
import { IncomeKind } from "@/types";
import { TKey as I18nKey, useI18n } from "@/lib/i18n";
import { createIncome } from "@/lib/api";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Modal from "./Modal";

interface Props {
  onClose: () => void;
  onSaved: () => void;
}

const fieldLabel = "mb-1 block text-xs font-bold uppercase tracking-wide text-muted";
const KINDS: IncomeKind[] = ["SALARY", "BENEFIT", "OTHER"];

export default function AddIncomeModal({ onClose, onSaved }: Props) {
  const { t } = useI18n();
  const [name, setName] = useState("");
  const [amount, setAmount] = useState("");
  const [kind, setKind] = useState<IncomeKind>("SALARY");
  const [busy, setBusy] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    const value = parseFloat(amount.replace(",", "."));
    if (!name.trim() || !(value > 0)) return;
    setBusy(true);
    try {
      await createIncome({ name: name.trim(), amount: value, kind });
      onSaved();
      onClose();
    } finally {
      setBusy(false);
    }
  };

  return (
    <Modal title={t("finance.new_income")} onClose={onClose}>
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
            <label className={fieldLabel}>{t("finance.form.income_kind")}</label>
            <select
              value={kind}
              onChange={(e) => setKind(e.target.value as IncomeKind)}
              className="w-full rounded-xl border border-line bg-elevated px-4 py-2.5 text-foreground transition-colors focus:border-secondary"
            >
              {KINDS.map((k) => (
                <option key={k} value={k}>
                  {t(`finance.income_kind.${k}` as I18nKey)}
                </option>
              ))}
            </select>
          </div>
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

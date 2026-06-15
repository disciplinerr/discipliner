"use client";

import { useState } from "react";
import { useI18n } from "@/lib/i18n";
import { createGoal } from "@/lib/api";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Modal from "./Modal";

interface Props {
  onClose: () => void;
  onSaved: () => void;
}

const fieldLabel = "mb-1 block text-xs font-bold uppercase tracking-wide text-muted";

export default function AddGoalModal({ onClose, onSaved }: Props) {
  const { t } = useI18n();
  const [name, setName] = useState("");
  const [target, setTarget] = useState("");
  const [current, setCurrent] = useState("");
  const [emoji, setEmoji] = useState("🎯");
  const [deadline, setDeadline] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    const targetValue = parseFloat(target.replace(",", "."));
    const currentValue = parseFloat((current || "0").replace(",", "."));
    if (!name.trim() || !(targetValue > 0)) return;
    setBusy(true);
    try {
      await createGoal({
        name: name.trim(),
        target_amount: targetValue,
        current_amount: currentValue >= 0 ? currentValue : 0,
        emoji: emoji.trim() || "🎯",
        color: "#4ade80",
        deadline: deadline || null,
      });
      onSaved();
      onClose();
    } finally {
      setBusy(false);
    }
  };

  return (
    <Modal title={t("finance.new_goal")} onClose={onClose}>
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-[4rem_1fr] gap-3">
          <div>
            <label className={fieldLabel}>{t("finance.form.emoji")}</label>
            <Input value={emoji} onChange={(e) => setEmoji(e.target.value)} maxLength={4} />
          </div>
          <div>
            <label className={fieldLabel}>{t("finance.form.name")}</label>
            <Input value={name} onChange={(e) => setName(e.target.value)} autoFocus />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className={fieldLabel}>{t("finance.form.goal_target")}</label>
            <Input
              inputMode="decimal"
              value={target}
              onChange={(e) => setTarget(e.target.value)}
              placeholder="0,00"
            />
          </div>
          <div>
            <label className={fieldLabel}>{t("finance.form.goal_current")}</label>
            <Input
              inputMode="decimal"
              value={current}
              onChange={(e) => setCurrent(e.target.value)}
              placeholder="0,00"
            />
          </div>
        </div>

        <div>
          <label className={fieldLabel}>{t("finance.form.goal_deadline")}</label>
          <Input type="date" value={deadline} onChange={(e) => setDeadline(e.target.value)} />
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

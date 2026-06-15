"use client";

import { useEffect, useState } from "react";
import { BudgetGroup, Category } from "@/types";
import { TKey, useI18n } from "@/lib/i18n";
import {
  createCategory,
  deleteCategory,
  getCategories,
  updateCategory,
} from "@/lib/api";
import AppIcon, { IconKey } from "@/lib/icons";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import IconPicker from "./IconPicker";
import Modal from "./Modal";
import { X } from "lucide-react";

interface Props {
  onClose: () => void;
  onChanged: () => void;
}

const GROUPS: BudgetGroup[] = ["NEEDS", "WANTS", "SAVINGS"];

export default function CategoryManagerModal({ onClose, onChanged }: Props) {
  const { t } = useI18n();
  const [categories, setCategories] = useState<Category[]>([]);
  const [newName, setNewName] = useState("");
  const [newIcon, setNewIcon] = useState<IconKey>("tag");
  const [newGroup, setNewGroup] = useState<BudgetGroup>("NEEDS");
  const [busy, setBusy] = useState(false);

  const load = () => getCategories().then(setCategories).catch(() => {});
  useEffect(() => {
    load();
  }, []);

  const notify = () => {
    load();
    onChanged();
  };

  const saveBudget = async (c: Category, raw: string) => {
    const value = parseFloat(raw.replace(",", ".")) || 0;
    if (value === c.monthly_budget) return;
    await updateCategory(c.id, { monthly_budget: value });
    notify();
  };

  const saveGroup = async (c: Category, group: BudgetGroup) => {
    await updateCategory(c.id, { group });
    notify();
  };

  const remove = async (c: Category) => {
    await deleteCategory(c.id);
    notify();
  };

  const add = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim()) return;
    setBusy(true);
    try {
      await createCategory({
        name: newName.trim(),
        emoji: newIcon,
        group: newGroup,
      });
      setNewName("");
      setNewIcon("tag");
      notify();
    } finally {
      setBusy(false);
    }
  };

  const selectCls =
    "rounded-lg border border-line bg-elevated px-2 py-1 text-xs font-semibold text-foreground focus:border-secondary";

  return (
    <Modal title={t("finance.categories_title")} onClose={onClose}>
      <div className="space-y-2">
        {categories.map((c) => (
          <div
            key={c.id}
            className="flex flex-wrap items-center gap-2 rounded-xl border border-line bg-surface px-3 py-2"
          >
            <AppIcon name={c.emoji} size={18} color={c.color} />
            <span className="min-w-0 flex-1 truncate text-sm font-semibold">{c.name}</span>
            <select
              value={c.group}
              onChange={(e) => saveGroup(c, e.target.value as BudgetGroup)}
              className={selectCls}
            >
              {GROUPS.map((g) => (
                <option key={g} value={g}>
                  {t(`finance.group.${g}` as TKey)}
                </option>
              ))}
            </select>
            <input
              type="number"
              min={0}
              step="0.01"
              defaultValue={c.monthly_budget || ""}
              placeholder="0"
              onBlur={(e) => saveBudget(c, e.target.value)}
              className="w-24 rounded-lg border border-line bg-elevated px-2 py-1 text-xs text-foreground focus:border-secondary"
            />
            <button
              type="button"
              onClick={() => remove(c)}
              aria-label={t("finance.form.delete")}
              className="rounded-lg px-2 py-1 text-muted transition-colors hover:text-rose-400"
            >
              <X size={14} />
            </button>
          </div>
        ))}
      </div>

      <form onSubmit={add} className="mt-5 space-y-3 border-t border-line pt-4">
        <p className="text-xs font-bold uppercase tracking-wide text-muted">
          {t("finance.form.add_category")}
        </p>
        <div className="flex gap-2">
          <div className="w-16 shrink-0">
            <IconPicker value={newIcon} onChange={setNewIcon} />
          </div>
          <Input
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            placeholder={t("finance.form.name")}
            className="flex-1"
          />
        </div>
        <div className="flex gap-2">
          <select
            value={newGroup}
            onChange={(e) => setNewGroup(e.target.value as BudgetGroup)}
            className="flex-1 rounded-xl border border-line bg-elevated px-4 py-2.5 text-sm text-foreground focus:border-secondary"
          >
            {GROUPS.map((g) => (
              <option key={g} value={g}>
                {t(`finance.group.${g}` as TKey)}
              </option>
            ))}
          </select>
          <Button type="submit" disabled={busy}>
            {t("finance.form.save")}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

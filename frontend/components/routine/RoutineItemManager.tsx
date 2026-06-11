"use client";

import { FormEvent, useEffect, useState } from "react";
import {
  addRoutineItem,
  deleteRoutineItem,
  getRoutineItems,
  toggleRoutineItem,
} from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import { UserRoutineItem } from "@/types";

export default function RoutineItemManager({ onChanged }: { onChanged: () => void }) {
  const { t } = useI18n();
  const [items, setItems] = useState<UserRoutineItem[]>([]);
  const [label, setLabel] = useState("");
  const [busy, setBusy] = useState<string | null>(null); // item_key or "add"
  const [error, setError] = useState("");

  function load() {
    getRoutineItems().then(setItems).catch(() => {});
  }

  useEffect(load, []);

  async function handleAdd(e: FormEvent) {
    e.preventDefault();
    if (!label.trim()) return;
    setError("");
    setBusy("add");
    try {
      await addRoutineItem(label.trim());
      setLabel("");
      load();
      onChanged();
    } catch {
      setError(t("routine.item_add_failed"));
    } finally {
      setBusy(null);
    }
  }

  async function handleToggle(item: UserRoutineItem) {
    setError("");
    setBusy(item.item_key);
    try {
      await toggleRoutineItem(item.item_key, !item.is_active);
      load();
      onChanged();
    } catch {
      setError(t("routine.item_toggle_failed"));
    } finally {
      setBusy(null);
    }
  }

  async function handleDelete(item: UserRoutineItem) {
    setError("");
    setBusy(item.item_key);
    try {
      await deleteRoutineItem(item.item_key);
      load();
      onChanged();
    } catch {
      setError(t("routine.item_delete_failed"));
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="space-y-4">
      <p className="text-xs text-muted">{t("routine.manage_items_hint")}</p>

      <ul className="divide-y divide-line">
        {items.map((item) => (
          <li key={item.item_key} className="flex items-center justify-between gap-3 py-2.5">
            <div className="min-w-0">
              <p className={`text-sm font-semibold truncate ${item.is_active ? "text-foreground" : "text-muted line-through"}`}>
                {item.label}
              </p>
              <span className={`text-[10px] font-bold uppercase tracking-wider ${item.is_system ? "text-blue-400/70" : "text-amber-400/70"}`}>
                {item.is_system ? t("routine.item_system_badge") : t("routine.item_custom_badge")}
              </span>
            </div>
            <div className="flex shrink-0 items-center gap-1.5">
              <button
                type="button"
                onClick={() => handleToggle(item)}
                disabled={busy === item.item_key}
                className="rounded-full border border-line px-2.5 py-1 text-[11px] font-bold text-muted transition-colors hover:border-secondary hover:text-foreground disabled:opacity-40"
              >
                {item.is_active ? t("routine.item_active") : t("routine.item_inactive")}
              </button>
              {!item.is_system && (
                <button
                  type="button"
                  onClick={() => handleDelete(item)}
                  disabled={busy === item.item_key}
                  className="rounded-full border border-line px-2.5 py-1 text-[11px] font-bold text-red-400 transition-colors hover:border-red-400 disabled:opacity-40"
                >
                  {t("routine.item_delete")}
                </button>
              )}
            </div>
          </li>
        ))}
      </ul>

      {/* Add new item */}
      <form onSubmit={handleAdd} className="flex gap-2">
        <input
          type="text"
          value={label}
          onChange={(e) => setLabel(e.target.value)}
          maxLength={200}
          placeholder={t("routine.add_item_placeholder")}
          className="min-w-0 flex-1 rounded-xl border border-line bg-elevated px-4 py-2 text-sm text-foreground placeholder:text-muted transition-colors focus:border-secondary focus:outline-none"
        />
        <button
          type="submit"
          disabled={busy === "add" || !label.trim()}
          className="shrink-0 rounded-xl bg-foreground px-4 py-2 text-xs font-bold text-background transition-all hover:bg-neutral-300 disabled:opacity-40"
        >
          {t("routine.add_item_submit")}
        </button>
      </form>

      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  );
}

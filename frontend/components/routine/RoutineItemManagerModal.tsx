"use client";

import RoutineItemManager from "@/components/routine/RoutineItemManager";
import { useI18n } from "@/lib/i18n";

interface Props {
  onClose: () => void;
  onChanged: () => void;
}

export default function RoutineItemManagerModal({ onClose, onChanged }: Props) {
  const { t } = useI18n();

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center sm:items-center"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={onClose} />

      <div className="relative z-10 flex max-h-[88vh] w-full max-w-lg flex-col rounded-t-2xl sm:rounded-2xl border border-line bg-background shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-line px-6 py-4 shrink-0">
          <div>
            <h2 className="text-lg font-extrabold tracking-tight">{t("routine.manage_items")}</h2>
            <p className="text-xs text-muted">{t("routine.manage_items_hint")}</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg px-3 py-1.5 text-xs font-bold text-muted transition-colors hover:text-foreground hover:bg-elevated"
          >
            ✕
          </button>
        </div>

        {/* Body */}
        <div className="overflow-y-auto flex-1 px-6 py-5">
          <RoutineItemManager onChanged={onChanged} />
        </div>
      </div>
    </div>
  );
}

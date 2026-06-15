"use client";

import { useEffect, useRef, useState } from "react";
import AppIcon, { IconKey, PICKER_ICONS } from "@/lib/icons";

interface Props {
  value: IconKey;
  onChange: (key: IconKey) => void;
  /** Accent color applied to the selected icon (e.g. category color). */
  color?: string;
}

/** Dropdown grid of the app's icon set — replaces free-text emoji input. */
export default function IconPicker({ value, onChange, color }: Props) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onDocClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, [open]);

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="flex h-[42px] w-full items-center justify-center rounded-xl border border-line bg-elevated text-foreground transition-colors hover:border-secondary focus:border-secondary"
        aria-label="Selecionar ícone"
      >
        <AppIcon name={value} size={20} color={color} />
      </button>

      {open && (
        <div className="absolute left-0 z-20 mt-2 grid w-64 grid-cols-6 gap-1 rounded-xl border border-line bg-background p-2 shadow-2xl">
          {PICKER_ICONS.map((key) => {
            const active = key === value;
            return (
              <button
                key={key}
                type="button"
                onClick={() => {
                  onChange(key);
                  setOpen(false);
                }}
                className={`flex aspect-square items-center justify-center rounded-lg transition-colors ${
                  active
                    ? "bg-foreground/10 text-foreground"
                    : "text-secondary hover:bg-elevated hover:text-foreground"
                }`}
                title={key}
              >
                <AppIcon name={key} size={18} color={active ? color : undefined} />
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

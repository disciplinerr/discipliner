"use client";

import { useI18n } from "@/lib/i18n";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface Props {
  year: number;
  month: number; // 1..12
  onChange: (year: number, month: number) => void;
}

export default function MonthSelector({ year, month, onChange }: Props) {
  const { locale } = useI18n();

  const shift = (delta: number) => {
    const d = new Date(year, month - 1 + delta, 1);
    onChange(d.getFullYear(), d.getMonth() + 1);
  };

  const label = new Date(year, month - 1, 1).toLocaleDateString(
    locale === "pt-BR" ? "pt-BR" : "en-US",
    { month: "long", year: "numeric" },
  );

  return (
    <div className="flex items-center gap-2 rounded-full border border-line bg-surface p-1">
      <button
        type="button"
        onClick={() => shift(-1)}
        aria-label="previous month"
        className="rounded-full p-1.5 text-secondary transition-colors hover:bg-elevated hover:text-foreground"
      >
        <ChevronLeft size={16} />
      </button>
      <span className="min-w-[8rem] text-center text-sm font-bold capitalize">{label}</span>
      <button
        type="button"
        onClick={() => shift(1)}
        aria-label="next month"
        className="rounded-full p-1.5 text-secondary transition-colors hover:bg-elevated hover:text-foreground"
      >
        <ChevronRight size={16} />
      </button>
    </div>
  );
}

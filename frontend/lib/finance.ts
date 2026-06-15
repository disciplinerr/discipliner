import { Locale } from "./i18n";

/** Format a number as currency. BRL for pt-BR, USD for en — matches the app locale. */
export function formatMoney(value: number, locale: Locale): string {
  const config =
    locale === "pt-BR"
      ? { locale: "pt-BR", currency: "BRL" }
      : { locale: "en-US", currency: "USD" };
  return new Intl.NumberFormat(config.locale, {
    style: "currency",
    currency: config.currency,
    minimumFractionDigits: 2,
  }).format(value);
}

/** Clamp a 0..1 ratio to a percentage, capped at 100 for bar widths. */
export function pct(spent: number, budget: number): number {
  if (budget <= 0) return 0;
  return Math.min(100, Math.round((spent / budget) * 100));
}

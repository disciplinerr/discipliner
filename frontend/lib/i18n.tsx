"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import { en } from "@/locales/en";
import { ptBR } from "@/locales/pt-BR";

export type Locale = "pt-BR" | "en";
export type TKey = keyof typeof ptBR;

const DICTS: Record<Locale, Record<TKey, string>> = { "pt-BR": ptBR, en };
const STORAGE_KEY = "discipliner_locale";
const DEFAULT_LOCALE: Locale = "pt-BR";

interface I18nContextValue {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: (key: TKey) => string;
}

const I18nContext = createContext<I18nContextValue>({
  locale: DEFAULT_LOCALE,
  setLocale: () => {},
  t: (key) => ptBR[key],
});

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>(DEFAULT_LOCALE);

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === "pt-BR" || stored === "en") setLocaleState(stored);
  }, []);

  const setLocale = useCallback((next: Locale) => {
    setLocaleState(next);
    localStorage.setItem(STORAGE_KEY, next);
  }, []);

  const t = useCallback((key: TKey) => DICTS[locale][key] ?? ptBR[key], [locale]);

  return (
    <I18nContext.Provider value={{ locale, setLocale, t }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n(): I18nContextValue {
  return useContext(I18nContext);
}

/** Translate a backend routine item_key; falls back to the backend label. */
export function routineLabel(
  t: (key: TKey) => string,
  itemKey: string,
  fallback: string
): string {
  const key = `routine.item.${itemKey}` as TKey;
  return key in ptBR ? t(key) : fallback;
}

"use client";

import { useCallback } from "react";
import { useSettingsStore, type Language } from "@/store/settings-store";
import { translations, type Locale } from "./translations";

export function useTranslation() {
  const locale = useSettingsStore((s) => s.settings.defaultLanguage) as Locale;
  const setSetting = useSettingsStore((s) => s.setSetting);

  const t = translations[locale] ?? translations.en;

  const setLocale = useCallback(
    (lang: Language) => setSetting("defaultLanguage", lang),
    [setSetting]
  );

  const format = useCallback((template: string, vars: Record<string, string>) => {
    return Object.entries(vars).reduce(
      (acc, [key, value]) => acc.replace(new RegExp(`\\{${key}\\}`, "g"), value),
      template
    );
  }, []);

  return { t, locale, setLocale, format };
}

export { translations };
export type { Locale };

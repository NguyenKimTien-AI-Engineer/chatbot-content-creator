"use client";

import { useEffect } from "react";
import { useSettingsStore } from "@/store/settings-store";

export function LocaleSync() {
  const locale = useSettingsStore((s) => s.settings.defaultLanguage);

  useEffect(() => {
    document.documentElement.lang = locale === "vi" ? "vi" : "en";
  }, [locale]);

  return null;
}

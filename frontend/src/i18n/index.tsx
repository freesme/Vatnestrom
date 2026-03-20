import { createContext, useContext, useState, useCallback, type ReactNode } from "react";
import zh from "./zh";
import en from "./en";

export type Lang = "zh" | "en";

const messages: Record<Lang, Record<string, string>> = { zh, en };

interface I18nContextValue {
  lang: Lang;
  setLang: (lang: Lang) => void;
  t: (key: string, fallback?: string) => string;
}

const I18nContext = createContext<I18nContextValue>(null!);

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<Lang>(() => {
    const saved = localStorage.getItem("lang");
    return saved === "en" ? "en" : "zh";
  });

  const changeLang = useCallback((l: Lang) => {
    setLang(l);
    localStorage.setItem("lang", l);
  }, []);

  const t = useCallback(
    (key: string, fallback?: string) => messages[lang][key] ?? fallback ?? key,
    [lang],
  );

  return (
    <I18nContext.Provider value={{ lang, setLang: changeLang, t }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  return useContext(I18nContext);
}

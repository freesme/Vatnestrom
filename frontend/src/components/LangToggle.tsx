import { useI18n } from "../i18n";

export default function LangToggle() {
  const { lang, setLang } = useI18n();

  return (
    <button
      className="fixed top-4 right-4 z-50 rounded-lg border border-dark-border bg-dark-card px-3 py-1.5 text-xs font-semibold text-text-secondary transition-colors hover:bg-dark-card-hover hover:text-text-primary"
      onClick={() => setLang(lang === "zh" ? "en" : "zh")}
    >
      {lang === "zh" ? "EN" : "中文"}
    </button>
  );
}

import { useI18n } from "../i18n";

export default function LangToggle() {
  const { lang, setLang } = useI18n();

  return (
    <button
      className="global-lang-toggle"
      onClick={() => setLang(lang === "zh" ? "en" : "zh")}
    >
      {lang === "zh" ? "EN" : "中文"}
    </button>
  );
}

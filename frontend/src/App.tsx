import { BrowserRouter, Routes, Route } from "react-router-dom";
import { I18nProvider } from "./i18n";
import StrategyList from "./pages/StrategyList";
import StrategyPage from "./pages/StrategyPage";
import LangToggle from "./components/LangToggle";
import "./App.css";

function App() {
  return (
    <I18nProvider>
      <BrowserRouter>
        <LangToggle />
        <Routes>
          <Route path="/" element={<StrategyList />} />
          <Route path="/strategy/:id" element={<StrategyPage />} />
        </Routes>
      </BrowserRouter>
    </I18nProvider>
  );
}

export default App;

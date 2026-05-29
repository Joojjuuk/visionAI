import { useState, useEffect, useMemo, useCallback } from "react";
import TopBar from "./components/TopBar.jsx";
import TweaksPanel, { TweakSection, TweakRadio, useTweaks } from "./components/TweaksPanel.jsx";
import UploadScreen from "./screens/UploadScreen.jsx";
import LoadingScreen from "./screens/LoadingScreen.jsx";
import ResultsScreen from "./screens/ResultsScreen.jsx";

const TWEAK_DEFAULTS = {
  theme: "light",
  markingStyle: "outline",
  showTags: true,
};

export default function App() {
  const [tweaks, setTweak] = useTweaks(TWEAK_DEFAULTS);
  const [stage, setStage] = useState("upload"); // upload | loading | results
  const [file, setFile] = useState(null);        // File object from input
  const [result, setResult] = useState(null);    // API response

  // Apply theme token to <html>
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", tweaks.theme);
  }, [tweaks.theme]);

  const toggleTheme = useCallback(() => {
    setTweak("theme", tweaks.theme === "dark" ? "light" : "dark");
  }, [tweaks.theme, setTweak]);

  const onAnalyze = useCallback((f) => {
    setFile(f);
    setStage("loading");
    setResult(null);
  }, []);

  const onDone = useCallback((apiResult) => {
    setResult(apiResult);
    setStage("results");
  }, []);

  const onReset = useCallback(() => {
    setStage("upload");
    setFile(null);
    setResult(null);
  }, []);

  const status = useMemo(() => {
    if (stage === "loading") return "Processando · YOLOv8 + Gemini";
    if (stage === "results") return "Análise concluída";
    return "YOLOv8 + Google Gemini";
  }, [stage]);

  return (
    <div className="app" data-screen-label={stage}>
      <TopBar theme={tweaks.theme} onToggleTheme={toggleTheme} status={status} />

      {stage === "upload" && <UploadScreen onAnalyze={onAnalyze} />}
      {stage === "loading" && <LoadingScreen file={file} onDone={onDone} />}
      {stage === "results" && (
        <ResultsScreen
          file={file}
          result={result}
          onReset={onReset}
          markingStyle={tweaks.markingStyle}
          showTags={tweaks.showTags}
        />
      )}

      <TweaksPanel title="Tweaks">
        <TweakSection label="Aparência">
          <TweakRadio
            label="Tema"
            value={tweaks.theme}
            onChange={(v) => setTweak("theme", v)}
            options={[
              { value: "light", label: "Claro" },
              { value: "dark", label: "Escuro" },
            ]}
          />
        </TweakSection>
        <TweakSection label="Marcações">
          <TweakRadio
            label="Estilo"
            value={tweaks.markingStyle}
            onChange={(v) => setTweak("markingStyle", v)}
            options={[
              { value: "outline", label: "Contorno" },
              { value: "filled", label: "Caixa" },
            ]}
          />
          <TweakRadio
            label="Rótulos"
            value={tweaks.showTags ? "on" : "off"}
            onChange={(v) => setTweak("showTags", v === "on")}
            options={[
              { value: "on", label: "Visíveis" },
              { value: "off", label: "Ocultos" },
            ]}
          />
        </TweakSection>
      </TweaksPanel>
    </div>
  );
}

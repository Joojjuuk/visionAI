/* global React, ReactDOM, TopBar, UploadScreen, LoadingScreen, ResultsScreen,
          TweaksPanel, TweakSection, TweakRadio, useTweaks */
const { useState, useEffect, useMemo } = React;

const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "theme": "light",
  "markingStyle": "outline",
  "showTags": true
}/*EDITMODE-END*/;

function App() {
  const [tweaks, setTweak] = useTweaks(TWEAK_DEFAULTS);

  // App state machine: upload → loading → results
  const [stage, setStage] = useState("upload");
  const [file, setFile] = useState(null);

  // Apply theme to <html data-theme=...>
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", tweaks.theme);
  }, [tweaks.theme]);

  const toggleTheme = () => {
    setTweak("theme", tweaks.theme === "dark" ? "light" : "dark");
  };

  const onAnalyze = (f) => {
    setFile(f);
    setStage("loading");
  };
  const onDone = () => setStage("results");
  const onReset = () => {
    setStage("upload");
    setFile(null);
  };

  const status = useMemo(() => {
    if (stage === "loading") return "Processando · local";
    if (stage === "results") return "Análise concluída · local";
    return "Local · YOLOv8 + LLaVA";
  }, [stage]);

  return (
    <div className="app" data-screen-label={`${stage}`}>
      <TopBar theme={tweaks.theme} onToggleTheme={toggleTheme} status={status} />

      {stage === "upload" && (
        <UploadScreen onAnalyze={onAnalyze} />
      )}
      {stage === "loading" && (
        <LoadingScreen file={file} onDone={onDone} />
      )}
      {stage === "results" && (
        <ResultsScreen
          file={file}
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
              { value: "dark",  label: "Escuro" },
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
              { value: "filled",  label: "Caixa" },
            ]}
          />
          <TweakRadio
            label="Rótulos"
            value={tweaks.showTags ? "on" : "off"}
            onChange={(v) => setTweak("showTags", v === "on")}
            options={[
              { value: "on",  label: "Visíveis" },
              { value: "off", label: "Ocultos" },
            ]}
          />
        </TweakSection>
      </TweaksPanel>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);

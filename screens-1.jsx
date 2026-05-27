/* global React, Icon, BrandMark, ScenePlaceholder */
const { useState: useState_s, useEffect: useEffect_s, useRef: useRef_s, useCallback: useCallback_s, useMemo: useMemo_s } = React;

/* ====================================================================
 * Upload Screen
 * ==================================================================== */
function UploadScreen({ onAnalyze }) {
  const [dragging, setDragging] = useState_s(false);
  const [file, setFile] = useState_s(null); // {name, size}
  const inputRef = useRef_s(null);

  const handleFile = useCallback_s((f) => {
    if (!f) return;
    setFile({ name: f.name, size: f.size });
  }, []);

  const onDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files?.[0];
    if (f) handleFile(f);
  };

  const onPick = (e) => {
    const f = e.target.files?.[0];
    if (f) handleFile(f);
  };

  const usePlaceholder = () => {
    setFile({ name: "canteiro_obras_demo.jpg", size: 1842000 });
  };

  const fmtSize = (b) => {
    if (b < 1024) return `${b} B`;
    if (b < 1024 * 1024) return `${(b/1024).toFixed(0)} KB`;
    return `${(b/(1024*1024)).toFixed(1)} MB`;
  };

  return (
    <section className="upload-screen fade-in">
      <div className="upload-hero">
        <div className="eyebrow">
          <span style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--brand)", display: "inline-block" }}></span>
          MVP · processamento 100% local
        </div>
        <h1>Detecção de <em>EPI</em> em imagens de obra.</h1>
        <p>Envie uma foto do ambiente de trabalho. O VisionAI identifica cada pessoa na cena e indica quem está em conformidade com capacete e colete refletivo.</p>
      </div>

      <div
        className={`dropzone ${dragging ? "is-dragging" : ""} ${file ? "has-file" : ""}`}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
      >
        {!file ? (
          <>
            <div className="dropzone-icon"><Icon.Upload /></div>
            <h3>Arraste uma foto ou{" "}
              <button className="file-link" onClick={() => inputRef.current?.click()}>selecione do computador</button>
            </h3>
            <p className="dz-sub">JPG, PNG ou WebP até 10MB · uma imagem por vez</p>
            <div className="dz-meta">
              <span>FORMATOS: JPG · PNG · WEBP</span>
              <span>MAX: 10MB</span>
              <span>RESOLUÇÃO: até 4096px</span>
            </div>
            <input
              ref={inputRef}
              type="file"
              accept="image/*"
              style={{ display: "none" }}
              onChange={onPick}
            />
            <button
              className="btn-ghost btn"
              style={{ marginTop: 8, fontSize: 12, padding: "8px 14px" }}
              onClick={usePlaceholder}
            >
              ou usar imagem de demonstração →
            </button>
          </>
        ) : (
          <>
            <div className="preview-row">
              <div className="preview-thumb">
                <ScenePlaceholder />
              </div>
              <div className="preview-meta">
                <div className="name">{file.name}</div>
                <div className="size">{fmtSize(file.size)} · pronto para análise</div>
              </div>
              <button className="btn-icon" onClick={() => setFile(null)} title="Remover">
                <Icon.X />
              </button>
            </div>
          </>
        )}
      </div>

      <div className="upload-cta">
        <button
          className="btn btn-primary"
          disabled={!file}
          onClick={() => file && onAnalyze(file)}
        >
          Analisar imagem
          <Icon.Arrow />
        </button>
      </div>

      <div className="feature-row">
        <div className="feature">
          <span className="num">01</span>
          <span className="label">Detecção de pessoas</span>
          <span className="desc">YOLOv8 identifica todas as pessoas presentes e isola cada região da cena.</span>
        </div>
        <div className="feature">
          <span className="num">02</span>
          <span className="label">Análise por pessoa</span>
          <span className="desc">LLaVA verifica individualmente a presença de capacete e colete refletivo.</span>
        </div>
        <div className="feature">
          <span className="num">03</span>
          <span className="label">Visualização imediata</span>
          <span className="desc">Sobreposição colorida com painel resumo e descrição do que está faltando.</span>
        </div>
      </div>
    </section>
  );
}

/* ====================================================================
 * Loading Screen
 * ==================================================================== */
const STEPS = [
  { id: "decode",   label: "Decodificando imagem",   duration: 600 },
  { id: "people",   label: "Detectando pessoas na imagem", duration: 1400 },
  { id: "epi",      label: "Analisando uso de EPI",  duration: 2400 },
  { id: "compile",  label: "Consolidando resultados", duration: 500 }
];

function LoadingScreen({ file, onDone }) {
  const [progress, setProgress] = useState_s(0);
  const [stepIdx, setStepIdx] = useState_s(0);
  const [log, setLog] = useState_s([]);
  const [discovered, setDiscovered] = useState_s([]);

  // simulate the pipeline
  useEffect_s(() => {
    const total = STEPS.reduce((a, s) => a + s.duration, 0);
    const start = performance.now();

    // log timeline
    const logTimeline = [
      { at: 0,    type: "ok",    text: "→ carregando modelos locais…" },
      { at: 200,  type: "ok",    text: "  yolov8n.pt  (6.7MB) carregado" },
      { at: 350,  type: "ok",    text: "  llava:7b    ollama-served" },
      { at: 700,  type: "brand", text: "▶ executando yolov8.detect()" },
      { at: 1100, type: "ok",    text: "  6 pessoas detectadas" },
      { at: 1400, type: "ok",    text: "  bboxes calculadas · 96.3% conf média" },
      { at: 1500, type: "brand", text: "▶ recortando regiões para LLaVA" },
      { at: 1700, type: "ok",    text: "  person_01 → analisando…" },
      { at: 2050, type: "ok",    text: "  person_01 ✓ capacete · ✓ colete" },
      { at: 2200, type: "ok",    text: "  person_02 → analisando…" },
      { at: 2500, type: "ok",    text: "  person_02 ✗ capacete · ✓ colete" },
      { at: 2700, type: "ok",    text: "  person_03 ✓ capacete · ✓ colete" },
      { at: 3000, type: "ok",    text: "  person_04 ✓ capacete · ✗ colete" },
      { at: 3300, type: "ok",    text: "  person_05 ✓ capacete · ✓ colete" },
      { at: 3700, type: "ok",    text: "  person_06 ✓ capacete · ✓ colete" },
      { at: 4500, type: "brand", text: "▶ consolidando relatório…" },
      { at: 4800, type: "ok",    text: "  análise concluída em 4.8s" },
    ];
    const logged = new Set();

    // animation frame
    let raf;
    const tick = () => {
      const elapsed = performance.now() - start;
      const pct = Math.min(1, elapsed / total);
      setProgress(pct);

      // advance step
      let acc = 0;
      let idx = 0;
      for (let i = 0; i < STEPS.length; i++) {
        if (elapsed >= acc) idx = i;
        acc += STEPS[i].duration;
      }
      setStepIdx(idx);

      // emit log entries
      logTimeline.forEach((entry, i) => {
        if (elapsed >= entry.at && !logged.has(i)) {
          logged.add(i);
          setLog(prev => [...prev, { ...entry, t: (entry.at/1000).toFixed(1) + "s" }]);
        }
      });

      // discover bounding boxes progressively
      const D = window.DETECTIONS;
      const peopleStart = 700, peopleEnd = 1400;
      if (elapsed >= peopleStart) {
        const slice = Math.min(D.length, Math.ceil((elapsed - peopleStart) / ((peopleEnd - peopleStart) / D.length)));
        setDiscovered(D.slice(0, slice));
      }

      if (elapsed < total + 200) {
        raf = requestAnimationFrame(tick);
      } else {
        setTimeout(onDone, 250);
      }
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [onDone]);

  return (
    <section className="loading-screen fade-in">
      <div className="loading-stage">
        <div className="loading-image-wrap">
          <div style={{ position: "relative", aspectRatio: "16 / 10", width: "calc(100% - 64px)", maxHeight: "calc(100% - 64px)" }}>
            <ScenePlaceholder />
            <div className="scan-line"></div>
            {discovered.map(p => (
              <div
                key={p.id}
                className="detection-marker"
                style={{
                  left: `${p.x}%`, top: `${p.y}%`,
                  width: `${p.w}%`, height: `${p.h}%`,
                }}
              >
                <span className="marker-pulse"></span>
                <span className="marker-tag">#{String(p.id).padStart(2, "0")}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <aside className="loading-side">
        <div className="loading-card">
          <div className="eyebrow" style={{ marginBottom: 14 }}>processando · {file?.name || "imagem.jpg"}</div>
          <h2>Analisando uso de EPI</h2>
          <p className="subtle">Modelos rodando localmente — sua imagem não sai deste computador.</p>

          <ol className="steps">
            {STEPS.map((s, i) => {
              const state = i < stepIdx ? "is-done" : i === stepIdx ? "is-active" : "";
              return (
                <li key={s.id} className={`step ${state}`}>
                  <span className="step-num">
                    {i < stepIdx ? <Icon.Check /> : i + 1}
                  </span>
                  <span className="step-label">{s.label}</span>
                  <span className="step-meta">
                    {i < stepIdx ? "concluído" : i === stepIdx ? "em curso" : "aguardando"}
                  </span>
                </li>
              );
            })}
          </ol>

          <div className="progress">
            <div className="progress-bar" style={{ width: `${progress * 100}%` }}></div>
          </div>
          <div className="progress-meta">
            <span>{Math.round(progress * 100)}% concluído</span>
            <span>{((1 - progress) * 4.8).toFixed(1)}s restantes</span>
          </div>
        </div>

        <div className="loading-card log-card">
          <div className="log-title">
            <h3>Log do pipeline</h3>
            <span className="eyebrow" style={{ fontSize: 10 }}>stderr</span>
          </div>
          <div className="log">
            {log.map((e, i) => (
              <div key={i} className={`log-entry ${e.type}`}>
                <span className="t">{e.t}</span>
                <span>{e.text}</span>
              </div>
            ))}
            {log.length > 0 && stepIdx < STEPS.length - 1 && (
              <div className="log-entry"><span className="t"></span><span style={{ opacity: 0.6 }}>▌</span></div>
            )}
          </div>
        </div>
      </aside>
    </section>
  );
}

window.UploadScreen = UploadScreen;
window.LoadingScreen = LoadingScreen;

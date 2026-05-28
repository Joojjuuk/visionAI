import { useState, useEffect, useRef } from "react";
import { Icon } from "../components/Icons.jsx";

const STEPS = [
  { id: "decode",  label: "Decodificando imagem",        weight: 0.05 },
  { id: "people",  label: "Detectando pessoas na imagem", weight: 0.35 },
  { id: "epi",     label: "Analisando uso de EPI",        weight: 0.50 },
  { id: "compile", label: "Consolidando resultados",       weight: 0.10 },
];

export default function LoadingScreen({ file, onDone }) {
  const [progress, setProgress] = useState(0);
  const [stepIdx, setStepIdx] = useState(0);
  const [log, setLog] = useState([]);
  const logRef = useRef(null);
  const abortRef = useRef(null);

  useEffect(() => {
    if (!file) return;

    abortRef.current = new AbortController();
    const { signal } = abortRef.current;

    // ── Fake progress animation while API call is running ──────────────────
    const startTime = performance.now();
    const FAKE_DURATION = 15000; // assume up to 15s; real result will cut it short
    let raf;

    const tick = () => {
      const elapsed = performance.now() - startTime;
      const pct = Math.min(0.92, elapsed / FAKE_DURATION); // cap at 92% until done
      setProgress(pct);

      let acc = 0;
      for (let i = 0; i < STEPS.length; i++) {
        acc += STEPS[i].weight;
        if (pct <= acc) { setStepIdx(i); break; }
      }

      if (!signal.aborted) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);

    // ── Initial log messages ───────────────────────────────────────────────
    const addLog = (type, text, delay) =>
      setTimeout(() => {
        if (signal.aborted) return;
        setLog((prev) => [...prev, { type, text, t: (delay / 1000).toFixed(1) + "s" }]);
      }, delay);

    addLog("brand", "→ carregando modelos locais…", 0);
    addLog("ok",    "  yolov8n.pt  pronto",          300);
    addLog("ok",    "  llama3.2-vision ollama-served", 600);
    addLog("brand", "▶ executando yolov8.detect()",  900);

    // ── Real API call ──────────────────────────────────────────────────────
    const formData = new FormData();
    formData.append("file", file);

    fetch("/api/analyze", { method: "POST", body: formData, signal })
      .then(async (res) => {
        if (!res.ok) {
          const err = await res.json().catch(() => ({ detail: res.statusText }));
          throw new Error(err.detail || "Erro no servidor");
        }
        return res.json();
      })
      .then((data) => {
        cancelAnimationFrame(raf);
        setProgress(1);
        setStepIdx(STEPS.length - 1);

        const n = data.detections?.length ?? 0;
        setLog((prev) => [
          ...prev,
          { type: "ok", text: `  ${n} pessoas detectadas`, t: "–" },
          { type: "brand", text: "▶ análise de EPI concluída", t: "–" },
          { type: "ok", text: `  relatório gerado em ${data.duration_seconds}s`, t: "–" },
        ]);

        setTimeout(() => onDone(data), 600);
      })
      .catch((err) => {
        if (err.name === "AbortError") return;
        cancelAnimationFrame(raf);
        setLog((prev) => [
          ...prev,
          { type: "error", text: `✗ Erro: ${err.message}`, t: "–" },
        ]);
      });

    return () => {
      abortRef.current?.abort();
      cancelAnimationFrame(raf);
    };
  }, [file, onDone]);

  // Auto-scroll log
  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [log]);

  return (
    <section className="loading-screen fade-in">
      <div className="loading-stage">
        <div className="loading-image-wrap">
          <div style={{ position: "relative", width: "calc(100% - 64px)", aspectRatio: "16 / 10" }}>
            {file && (
              <img
                src={URL.createObjectURL(file)}
                alt="Imagem sendo processada"
                style={{ width: "100%", height: "100%", objectFit: "cover", borderRadius: 8, display: "block" }}
              />
            )}
            <div className="scan-line" />
          </div>
        </div>
      </div>

      <aside className="loading-side">
        <div className="loading-card">
          <div className="eyebrow" style={{ marginBottom: 14 }}>
            processando · {file?.name || "imagem.jpg"}
          </div>
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
            <div className="progress-bar" style={{ width: `${progress * 100}%` }} />
          </div>
          <div className="progress-meta">
            <span>{Math.round(progress * 100)}% concluído</span>
          </div>
        </div>

        <div className="loading-card log-card">
          <div className="log-title">
            <h3>Log do pipeline</h3>
            <span className="eyebrow" style={{ fontSize: 10 }}>stderr</span>
          </div>
          <div className="log" ref={logRef}>
            {log.map((e, i) => (
              <div key={i} className={`log-entry ${e.type}`}>
                <span className="t">{e.t}</span>
                <span>{e.text}</span>
              </div>
            ))}
            {log.length > 0 && stepIdx < STEPS.length - 1 && (
              <div className="log-entry">
                <span className="t" />
                <span style={{ opacity: 0.6 }}>▌</span>
              </div>
            )}
          </div>
        </div>
      </aside>
    </section>
  );
}

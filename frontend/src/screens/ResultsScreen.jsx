import { useState, useEffect, useMemo } from "react";
import { Icon } from "../components/Icons.jsx";
import BoundingBoxes from "../components/BoundingBoxes.jsx";

function computeStatus(p) {
  const helmetOk = p.helmet;
  const vestOk = p.vest;
  const glassesOk = p.glasses !== undefined ? p.glasses : true;
  const capAlert = p.cap === true;

  const ok = helmetOk && vestOk && glassesOk && !capAlert;
  const missing = [];
  if (!p.helmet) missing.push("capacete");
  if (!p.vest) missing.push("colete");
  if (p.glasses === false) missing.push("óculos");
  if (p.cap === true) missing.push("boné (perigo)");

  return { ok, missing, helmetOk, vestOk, glassesOk, capAlert };
}


export default function ResultsScreen({ file, result, onReset, markingStyle, showTags }) {
  const detections = result?.detections ?? [];
  const stats = result?.stats ?? { total: 0, ok: 0, bad: 0, pct: 0, avg_confidence: 0 };
  const imageUrl = result?.image_url ?? null; // served by FastAPI /uploads/...

  const [activeId, setActiveId] = useState(null);
  const [hoverId, setHoverId] = useState(null);
  const [filter, setFilter] = useState("all"); // all | ok | bad

  useEffect(() => {
    const onKey = (e) => { if (e.key === "Escape") setActiveId(null); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const filtered = useMemo(() => {
    if (filter === "ok") return detections.filter((p) => computeStatus(p).ok);
    if (filter === "bad") return detections.filter((p) => !computeStatus(p).ok);
    return detections;
  }, [detections, filter]);

  // Build a local preview URL from the File if imageUrl isn't yet available
  const displaySrc = imageUrl || (file ? URL.createObjectURL(file) : null);

  return (
    <section className="results-screen fade-in">
      <div className="results-header">
        <div>
          <div className="breadcrumbs">
            <span>Análises</span>
            <span className="sep">/</span>
            <span className="current">{file?.name ?? "imagem"}</span>
          </div>
          <h1 style={{ marginTop: 6 }}>Resultado da análise</h1>
        </div>
        <div className="header-actions">
          <button className="btn btn-ghost" onClick={onReset}>
            <Icon.Reload /> Analisar nova imagem
          </button>
        </div>
      </div>

      {/* ── Image Panel ── */}
      <div className="image-panel">
        <div className="image-toolbar">
          <div className="left">
            <span className="file">{file?.name ?? "imagem"}</span>
            {result?.image_width && (
              <span>{result.image_width} × {result.image_height}</span>
            )}
            {result?.duration_seconds && (
              <span>processado em {result.duration_seconds}s</span>
            )}
          </div>
          <div className="legend">
            <span className="legend-item">
              <span className="legend-dot ok" /> Conforme
            </span>
            <span className="legend-item">
              <span className="legend-dot bad" /> Sem EPI completo
            </span>
          </div>
        </div>

        <div className="image-stage">
          <div style={{ position: "relative", aspectRatio: "16 / 10", width: "calc(100% - 32px)", maxHeight: "calc(100% - 32px)" }}>
            {displaySrc && (
              <img
                src={displaySrc}
                alt="Resultado da análise"
                style={{ width: "100%", height: "100%", objectFit: "contain", display: "block", borderRadius: 6 }}
              />
            )}
            <BoundingBoxes
              detections={detections}
              activeId={activeId}
              hoverId={hoverId}
              onActivate={setActiveId}
              onHover={setHoverId}
              markingStyle={markingStyle}
              showTags={showTags}
            />
          </div>
        </div>
      </div>

      {/* ── Sidebar ── */}
      <aside className="sidebar">
        <div className="card">
          <div className="eyebrow" style={{ marginBottom: 14 }}>Resumo</div>
          <div className="stats-grid">
            <div className="stat">
              <span className="label">Total</span>
              <span className="value">{String(stats.total).padStart(2, "0")}</span>
            </div>
            <div className="stat ok">
              <span className="label">Conformes</span>
              <span className="value">{String(stats.ok).padStart(2, "0")}</span>
            </div>
            <div className="stat bad">
              <span className="label">Sem EPI</span>
              <span className="value">{String(stats.bad).padStart(2, "0")}</span>
            </div>
            <div className="stat">
              <span className="label">Avg. confidence</span>
              <span className="value">
                {stats.avg_confidence}
                <span style={{ fontSize: 14, color: "var(--text-muted)" }}>%</span>
              </span>
            </div>
          </div>

          <div className="compliance-bar">
            <div className="top">
              <h4>Conformidade da cena</h4>
              <span className="pct">{stats.pct}%</span>
            </div>
            <div className="bar-track">
              <div className="bar-seg ok" style={{ width: `${stats.pct}%` }} />
              <div className="bar-seg bad" style={{ width: `${100 - stats.pct}%` }} />
            </div>
            <div className="bar-meta">
              <span>{stats.ok} conforme</span>
              <span>{stats.bad} requerem atenção</span>
            </div>
          </div>
        </div>

        <div className="card persons-card">
          <div className="card-head">
            <h3>Pessoas detectadas</h3>
            <span className="count">{filtered.length} de {detections.length}</span>
          </div>

          <div className="filter-tabs" role="tablist">
            {[
              { key: "all", label: "Todas",    count: stats.total },
              { key: "bad", label: "Sem EPI",  count: stats.bad   },
              { key: "ok",  label: "Conformes", count: stats.ok   },
            ].map((t) => (
              <button
                key={t.key}
                className={`filter-tab ${filter === t.key ? "active" : ""}`}
                onClick={() => setFilter(t.key)}
              >
                {t.label}
                <span className="filter-count">{t.count}</span>
              </button>
            ))}
          </div>

          <ul className="person-list">
            {filtered.map((p) => {
              const { ok, missing, helmetOk, vestOk, glassesOk, capAlert } = computeStatus(p);
              const isActive = activeId === p.id;
              return (
                <li key={p.id}>
                  <button
                    className={`person ${isActive ? "is-active" : ""} ${ok ? "ok-state" : "bad-state"}`}
                    onClick={() => setActiveId(p.id === activeId ? null : p.id)}
                    onMouseEnter={() => setHoverId(p.id)}
                    onMouseLeave={() => setHoverId(null)}
                  >
                    <span className={`person-num ${ok ? "ok" : "bad"}`}>{p.id}</span>
                    <span className="person-body">
                      <span className="person-title">
                        {p.role}
                        <span className="eyebrow" style={{ fontSize: 10 }}>
                          {ok ? "CONFORME" : "ATENÇÃO"}
                        </span>
                      </span>
                      <span className="person-desc">
                        <span className={`epi-chip ${helmetOk ? "ok" : "bad"}`}>capacete</span>
                        <span className={`epi-chip ${vestOk ? "ok" : "bad"}`}>colete</span>
                        {p.glasses !== undefined && (
                          <span className={`epi-chip ${glassesOk ? "ok" : "bad"}`}>óculos</span>
                        )}
                        {p.cap !== undefined && (
                          <span className={`epi-chip ${capAlert ? "alert" : "ok"}`}>{capAlert ? "boné" : "sem boné"}</span>
                        )}
                        {!ok && (
                          <span style={{ color: "var(--danger)", fontSize: 11.5 }}>
                            requer: {missing.join(", ")}
                          </span>
                        )}
                      </span>
                    </span>
                    <span className="person-conf">{Math.round(p.confidence * 100)}%</span>
                  </button>
                </li>
              );
            })}
            {filtered.length === 0 && (
              <li style={{ padding: "32px 16px", textAlign: "center", color: "var(--text-faint)", fontSize: 13 }}>
                Nenhuma pessoa neste filtro.
              </li>
            )}
          </ul>
        </div>
      </aside>
    </section>
  );
}
